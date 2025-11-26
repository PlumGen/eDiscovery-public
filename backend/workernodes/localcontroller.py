from loadDLLs import add_dll_directories_from_site_packages
# Use it before importing any .pyd/.dll-based modules
dll_dirs = add_dll_directories_from_site_packages()
#print("🔗 DLL directories added:", dll_dirs) 

import argparse
import torch
from sqlalchemy import Table, Column, text, String, select, inspect, func, distinct
import os
from embedding_models import embedding_models
import requests
import json
import logging
import sys
import builtins
progress_table_name  = os.environ.get("DATATEXTTABLESTATUS")

# Set up logging to stdout
import builtins
import logging
import sys

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
log = logging.getLogger()
def log_print(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    file = kwargs.get("file", sys.stdout)
    flush = kwargs.get("flush", False)

    message = sep.join(str(a) for a in args) + end
    log.info(message.strip("\n"))  # Strip only final newline for cleaner log

    if flush and hasattr(file, "flush"):
        file.flush()
builtins.print = log_print


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def run_extract(db, bucketname, documentdump=False):
    
    print("Inside run_extract")  # Add this
    table_name = os.environ.get("RAWDATATEXTTABLE")
    engine = db.get_engine() 
    inspector = inspect(engine)
    # Check and create the table if it doesn't exist

    if inspector.has_table(table_name):
        db.create_schema_and_indexes()
    print('starting ingest')
    
    if documentdump=='table':
        from ingest_clean import main_ingestdata
        main_ingestdata.main_ingestdata(db, bucketnamegiven=bucketname) 
    elif documentdump=='document':
        from ingest_clean import main_ingestdocumentdump
        main_ingestdocumentdump.main_ingestdocumentdump(db, bucketnamegiven=bucketname) 

def run_clean(db):
    from ingest_clean import main_cleantext
    main_cleantext.main_cleantext(db)

def run_tokenize(db):
    from tokenizerlocal import main_tokenizetext
    main_tokenizetext.main_tokenizetext(db, embedding_models=embedding_models)

def run_embed(db):
    from embedizelocal import main_embed
    main_embed.main_embed(db, get_device())

def run_simpairs(db):
    from deduplicate import main_simpairs
    main_simpairs.main_simpairs(db) 
    
def run_deduplicate(db):
    from deduplicate import main_markedduplicates
    main_markedduplicates.main_markedduplicates(db)  
                
def run_runranking(db):
    from rank_cluster import main_runranking
    import RunCheck
    main_runranking.main_runranking(db, RunCheck)
                            
def run_cluster(db):
    from rank_cluster import main_cluster
    import RunCheck
    main_cluster.main_cluster(db, RunCheck)
    
def run_maincandidatelabel(db):
    from labelcandidates import main_candidatelabels
    
    main_candidatelabels.main_candidatelabels(db)
                
def run_disambiguations(db):
    
    print('Starting DisAmbiguation Cycles:')
    from cycleonCPU import process_entrypoint
    process_entrypoint(db)

            
def run_debug(db):
    print("🛠️ Debug mode: container is now sleeping indefinitely")
    import time
    while True:
        time.sleep(3600)


def reportbacktoFrontEnd(args_dict):            

    
    url = "http://ediscovery-frontend.default.svc.cluster.local:80/api/jobcompleted"

    response = requests.post(url, json=args_dict)

    print('From Worker Nodes, reporting job complete:') 
    print(response.status_code)
    print(response.text)

def trackEndofStageJob(db):
    try:
        with db.conn_read() as conn:
            unique_count = conn.execute(
                select(func.count(distinct(db.tables[progress_table_name].c.status_text)))
            ).scalar_one()
        return unique_count     
    except:return 0
            
def main():
    print("Inside Main Controller")  # Add this
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, help="Which pipeline stage to run")
    parser.add_argument("--db_name", required=True, help="Which project to access")
    parser.add_argument("--bucketname", required=False, help="Which project to extract/export")
    parser.add_argument("--documentdump", required=False, help="raw document ingestion versus tabulated data ingestion")    
    
    
    args = parser.parse_args()
    
    if args.db_name is None:
        print(f"db_name not valid: {args.db_name}")
        sys.exit(1)
    
    if (args.stage=='extract') or (args.stage=='export'):
        if args.bucketname is None or args.documentdump is None:
            print(f"Bucket Name needs to be identified: {args.bucketname}")
            print(f"documentdump flag needs to be identified: {args.documentdump}")            
            sys.exit(1)            
        else: 
            bucketname   = args.bucketname
            documentdump = args.documentdump
        
    from database_manager import DatabaseManager 
    db = DatabaseManager(db_name=args.db_name)
    
    dispatch = {
        "extract": run_extract, #cpu
        "clean": run_clean, #cpu
        "tokenize": run_tokenize, #cpu
        "embed": run_embed, #gpu
        "simpairs":run_simpairs, #cpu
        ##ask user for duplication definition
        "deduplicate":run_deduplicate, #cpu
        "run_runranking":run_runranking, #gpu
        "cluster": run_cluster, #gpu
        "candidatelabel":run_maincandidatelabel, #cpu
        ##ask user to label the candidates
        "disambiguations":run_disambiguations,
        "debug": run_debug  # <-- Add this line
    }
    if args.stage not in dispatch:
        print(f"Unknown stage: {args.stage}")
        sys.exit(1)

    try:
        initialCompletedStages = trackEndofStageJob(db)
        if (args.stage=='extract') or (args.stage=='export'):
            dispatch[args.stage](db, bucketname, documentdump)
        else:    
            dispatch[args.stage](db)
            
        args_dict = vars(args)
        currentCompletedStages = trackEndofStageJob(db)
        
        # don't recall unless the complete flag is generated
        if currentCompletedStages>initialCompletedStages:
            reportbacktoFrontEnd(args_dict)
                    
    except Exception as e:
        print(f"❌ Error in stage '{args.stage}': {e}")
        import traceback
        traceback.print_exc()
            
    finally:
        # Force shutdown of database connections

        db.engine.dispose()
        
        ## once the execution is complete, make a call back to the front API
        #http://ediscovery-frontend.default.svc.cluster.local:80/api/jobcompleted
        


        # Optional: force termination if still lingering
        import os
        os._exit(0)

if __name__ == "__main__":
    main()
