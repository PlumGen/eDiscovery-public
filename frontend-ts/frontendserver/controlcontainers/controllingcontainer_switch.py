from sqlalchemy import Table, Column, text, String, select, inspect, distinct
import os
import time

from sqlalchemy import select, func


location = os.environ.get('CLOUDREGION')

if os.environ.get('CLOUDENV', '').upper() == 'AZURE':
    from . import calculate_parallel_jobs_azure as calculate_parallel_jobs
else:    
    from . import calculate_parallel_jobs as calculate_parallel_jobs

from . import jobconfigs


    
if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
progress_table_name  = os.environ.get("DATATEXTTABLESTATUS")

dispatch = {
    0:
        {
            'name':'extract',
            'compute':'neutral',
            'functionname':'run_extract',
            'parallel':False,
            'donotrunstage':{
                'status':["DATAINGESTCOMPLETE"],
                'tables':["RAWDATATEXTTABLE"]
            },
            'runstage':{
                'status':[],
                'tables':[]
            }

        },
    1:
        {
          'name':'clean',
          'compute':'neutral',
          'functionname':'run_clean',
          'parallel':False,
            'donotrunstage':{
                'status':["TEXTCLEANCOMPLETE"],
                'tables':["CLEANEDDATATEXTTABLE"]
            },
            'runstage':{
                'status':["DATAINGESTCOMPLETE"],
                'tables':["RAWDATATEXTTABLE"]
            }
        },

    2:
        {
          'name':'tokenize',
          'compute':'neutral',
          'functionname':'run_tokenize', 
          'parallel':False,
            'donotrunstage':{
                'status':["TOKENIZECOMPLETE:ALL"],
                'tables':["TOKENIZEDATATEXTTABLE"]
            },
            'runstage':{
                'status':["TEXTCLEANCOMPLETE"],
                'tables':["CLEANEDDATATEXTTABLE"]
            }
        },
        
    3:
        {
          'name':'embed',
          'compute':'gpu',
          'functionname':'run_embed', 
          'parallel':True,
          
            'donotrunstage':{
                'status':["EMBEDCOMPLETE:ALL"],
                'tables':["EMBEDDATATEXTTABLE"]
            },
            'runstage':{
                'status':["TOKENIZECOMPLETE:ALL"],
                'tables':["TOKENIZEDATATEXTTABLE"]
            }
        },
        
    4:
        {
          'name':'simpairs',
          'compute':'neutral',
          'functionname':'run_simpairs',  
          'parallel':False,          
            'donotrunstage':{
                'status':["SIMPAIRSCOMPLETE"],
                'tables':["SIMPAIRSDATATEXTTABLE"]
            },
            'runstage':{
                'status':["EMBEDCOMPLETE:ALL"],
                'tables':["EMBEDDATATEXTTABLE"]
            }
        },            

    5:
        {
          'name':'deduplicate',
          'compute':'neutral',
          'functionname':'run_deduplicate',  
          'parallel':False,
            'donotrunstage':{
                'status':["DUPLICATESMARKEDCOMPLETE"],
                'tables':["MARKEDDUPLICATESTEXTTABLE"]
            },
            'runstage':{
                'status':["%DUPLICATEDEFINITION%"],
                'tables':["SIMPAIRSDATATEXTTABLE"]
            }
        }, 
        
    6:
        {
          'name':'run_runranking',
          'compute':'gpu',
          'functionname':'run_runranking',
          'parallel':False,          
            'donotrunstage':{
                'status':["RANKINGCOMPLETE"],
                'tables':["RANKINGDATATEXTTABLE"]
            },
            'runstage':{
                'status':["DUPLICATESMARKEDCOMPLETE"],
                'tables':["MARKEDDUPLICATESTEXTTABLE"]
            }
        }, 

    7:
        {
          'name':'cluster',
          'compute':'gpu',
          'functionname':'run_cluster', 
          'parallel':False,
          
            'donotrunstage':{
                'status':["CLUSTERCOMPLETE:ALL"],
                'tables':["CLUSTERINGDATATEXTTABLE"]
            },
            'runstage':{
                'status':["EMBEDCOMPLETE:ALL"],
                'tables':["EMBEDDATATEXTTABLE"]
            }
        }, 

    8:
        {
          'name':'candidatelabel',
          'compute':'neutral',
          'functionname':'run_maincandidatelabel',  
          'parallel':False,
            'donotrunstage':{
                'status':["LABELCANDIDATECOMPLETE"],
                'tables':["LABELCANDIDATESTABLE", "LABELCANDIDATESVALIDATIONTABLE"]
            },
            'runstage':{
                'status':["EMBEDCOMPLETE:ALL", "CLUSTERCOMPLETE:ALL", "RANKINGCOMPLETE"],
                'tables':["EMBEDDATATEXTTABLE", "CLUSTERINGDATATEXTTABLE", "RANKINGDATATEXTTABLE"]
            }
        }, 

    9:
        {
          'name':'disambiguations',
          'compute':'cpu',
          'functionname':'run_disambiguations',  
          'parallel':True,
            'donotrunstage':{
                'status':["DISAMBIGUATIONCOMPLETE"],
                'tables':["MASTERNODELABELS"]
            },
            'runstage':{
                'status':["USERLABELEDNODES", "LABELCANDIDATECOMPLETE"],
                'tables':["LABELCANDIDATESTABLE", "LABELCANDIDATESVALIDATIONTABLE"]
            }
        }, 

}


def countparallelpods(db):
    
    count=1
    engine = db.get_engine() 
    inspector = inspect(engine)
    
    if inspector.has_table(os.environ.get("TOKENIZEDATATEXTTABLE")):
    ## or get a env variable that contains the number of models counts    
        with db.conn_read() as conn:
            count = conn.execute(
                select(func.count(distinct(db.tables[os.environ.get("TOKENIZEDATATEXTTABLE")].c.model_name)))
            ).scalar_one()

    return count

def statusExists(db, stringtocheck):
    engine = db.get_engine() 
    inspector = inspect(engine)
        
    result=False
    if inspector.has_table(progress_table_name):
        if "%" in stringtocheck:
            with db.conn_read() as conn:
                    result = conn.execute( 
                        select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text.like(stringtocheck))
                    ).first()
        else:
            with db.conn_read() as conn:
                result = conn.execute(
                    select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == stringtocheck)
                ).first()
    
    return result        


def runthisStage(db, bucketname, stagemeta, userinjesttype):
    
    print(f'Run This Stage --Main Switch: {stagemeta["name"]}')
    
    if os.environ.get('RUNENV')!='CUBE':
        print('Run in Docker Container')
        jobconfigs.run_locally(stagemeta["name"], db.engine.url.database, bucketname)
    elif os.environ.get('RUNENV')=='CUBE':
        print('Run in K8s')
        numpods = 1
        gpucount =0

        if stagemeta["compute"]=='gpu':gpucount =1
        if stagemeta["compute"]=='cpu':gpucount =-1        
        max_pods, cpuRequest, memoryRequest = calculate_parallel_jobs.calculate_parallel_pods(location=location, gpucount=gpucount)        
        if stagemeta['parallel']:
            numpods = max(min(int(countparallelpods(db)), max_pods),1)
        
        print(f'Running {numpods} replicas for this job')    
        for idx, jobcount in enumerate(range(numpods)):
            sleeptime=0
            if (idx==0):sendjob=True
            else:
                try:
                    checkjobstatus = jobconfigs.check_if_pod_running(stagemeta["name"]+f'_{idx-1}') 
                    if checkjobstatus=='running':sendjob=True
                except Exception as e:
                    print(e)
                    time.sleep(10*60)
                    sendjob=True            
            try:
                if sendjob:
                    jobconfigs.generate_k8_job(jobname=stagemeta["name"]+f'_{idx}', stage=stagemeta["name"], db_name=db.engine.url.database, bucketname=bucketname, userinjesttype=userinjesttype, RUNENV='CUBE', gpucount=gpucount, claimName='vpc', sleeptime=sleeptime, cpuRequest=cpuRequest, memoryRequest=memoryRequest)
                    sendjob=False
            except Exception as e:
                # this is to account for racing conditions where multiple calls are made to generate jobs
                # kubectl will not start jobs with the same name
                # and each job is interchangeable so there is no need to check further downstream
                print('Error in generating jobs')
                print(e)
                

        
def runworkerjobs(db=None, bucketname=None, userinjesttype=''):
    
    engine = db.get_engine() 
    inspector = inspect(engine)
    
    for stageid, stagemeta in dispatch.items():
        if stageid==0:
            if all([inspector.has_table(os.environ.get(requiredTable)) for requiredTable in stagemeta['donotrunstage']['tables']]):db.create_schema_and_indexes()
            if all([statusExists(db, status) for status in stagemeta['donotrunstage']['status']]):
                continue
            else:
                if userinjesttype!='':
                    ## if tables do not exist yet, and userinjesttype is document, then create schema
                    if not inspector.has_table(progress_table_name) and userinjesttype=='doument':db.create_schema_and_indexes()
                    runthisStage(db, bucketname, stagemeta, userinjesttype)
        if  stageid==0 and userinjesttype=='':
            continue    
        
        if not inspector.has_table(progress_table_name):
            return False    
        
        CheckstatusExists = all([statusExists(db, status) for status in stagemeta['donotrunstage']['status']])
        ChecktableExists  = all([inspector.has_table(os.environ.get(requiredTable)) for requiredTable in stagemeta['donotrunstage']['tables']])
            
        if CheckstatusExists and ChecktableExists:
            print(f'DO NOT RUN This Stage --Main Switch: {stagemeta["name"]}')
           
        
        else:
            DORUNCheckstatusExists = all([statusExists(db, status) for status in stagemeta['runstage']['status']])
            DORUNChecktableExists  = all([inspector.has_table(os.environ.get(requiredTable)) for requiredTable in stagemeta['runstage']['tables']])
            
            if DORUNCheckstatusExists and DORUNChecktableExists:runthisStage(db, bucketname, stagemeta, userinjesttype)
    
    engine.dispose()