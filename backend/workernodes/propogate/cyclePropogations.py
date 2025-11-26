import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd
import numpy as np
import os
from masternodes.trackLabeleledNodes import trackLabeleledNodes
from propogate.prePropogate import runPrePropogation
from masternodes.trackLPropNodes import trackLPropNodes
from propogate.ReverseprePropogate import ReverseprePropogate    
from masternodes.trackLRevPropNodes import trackLRevPropNodes 
from propogate.DisAmbiguate import DisAmbiguate
from masternodes.trackLDisAmbigNodes import trackLDisAmbigNodes 
import masternodes.taskManager as taskManager
import sys

from sqlalchemy import Table, Column, text, String, select, inspect, func
from sqlalchemy.dialects.postgresql import insert

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
   
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_rankingtable = os.environ.get("RANKINGDATATEXTTABLE")

progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))

embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))

rawtextdata   = os.environ.get("RAWDATATEXTTABLE")
cleantextdata = os.environ.get("CLEANEDDATATEXTTABLE")
table_name_tokenize  = os.environ.get("TOKENIZEDATATEXTTABLE")

table_name_cluster = os.environ.get("CLUSTERINGDATATEXTTABLE")
table_name_prepropogationtable = os.environ.get("PREPROPOGATEDLABELS")

def runNextPropogation(db, RunCheck):
    while True:
        with db.conn_read() as conn:
            propogated = conn.execute(
                select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "DISAMBIGUATIONCOMPLETE")
            ).first()            
        if propogated:
            print("DISAMBIGUATIONCOMPLETE already exists in progress table.")  
            sys.exit(1)
            return True
        
        nextTask = taskManager.GetNextTask(db)
        print('nextTask:', nextTask)

        if not nextTask:
            print("⚠️ No task returned — skipping.")
            return False

        match nextTask['Process']:
            case "L1_Propogation":
                if nextTask['model'] == 'All':
                    trackLPropNodes(db)
                    taskManager.markDone(db, nextTask['Process'], nextTask['model'])

                else:
                    runPrePropogation(db, RunCheck, [nextTask['model']])
                    taskManager.markDone(db, nextTask['Process'], nextTask['model'])

            case "Reverse_L1_Propogation":
                if nextTask['model'] == 'All':
                    trackLRevPropNodes(db)
                    taskManager.markDone(db, nextTask['Process'], nextTask['model'])

                else:
                    ReverseprePropogate(db, RunCheck, [nextTask['model']])
                    taskManager.markDone(db, nextTask['Process'], nextTask['model'])

            case "DisAmbiguation":
                if nextTask['model'] == 'All':
                    trackLDisAmbigNodes(db)
                    taskManager.markDone(db, nextTask['Process'], nextTask['model'])

                else:
                    DisAmbiguate(db, RunCheck, [nextTask['model']], taskManager=taskManager, stringtoPass=f"{nextTask['Process']}:{nextTask['model']}")
                    taskManager.markDone(db, nextTask['Process'], nextTask['model'])
                    nextTask = None