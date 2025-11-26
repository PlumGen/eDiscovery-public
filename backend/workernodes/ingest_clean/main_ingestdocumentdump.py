
from sqlalchemy import Table, Column, MetaData, String, select

from sqlalchemy import text, MetaData, Table, inspect
from sqlalchemy.dialects.postgresql import insert

import pandas as pd

import os
import hashlib


### Cloud Specific blob reads
from .readbuckets import azurebucket 
from .extractfromblob import DocumentExtractor
from concurrent.futures import ThreadPoolExecutor, as_completed
from .processblob import process_and_store

de = DocumentExtractor()
if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
BUCKETNAME = os.environ.get("BUCKETNAME")
table_name = os.environ.get("RAWDATATEXTTABLE")
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")

def main_ingestdocumentdump(db, bucketnamegiven=None, max_workers=8):
    engine = db.get_engine()     
    inspector = inspect(engine)

    if bucketnamegiven is None:
        bucketnamegiven = BUCKETNAME

    if not inspector.has_table(table_name):
        db.create_schema_and_indexes()

    listofblobs, container_client = azurebucket.getbloblist(container_name=bucketnamegiven)
    missing = []

    # up to 2 passes: first + one recheck
    for recheckCounter in range(2):
        try:
            query = f"SELECT blob_name FROM {table_name}"
            with db.conn_read() as conn:
                result = conn.execute(text(query))
                blob_name_injected = [r[0] for r in result.fetchall()]
        except Exception as e:
            print(e)
            blob_name_injected=[]
            
        missing = [x for x in listofblobs if x not in set(blob_name_injected)]

        if not missing:
            break  # nothing left to do

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_and_store, db, de, container_client, name): name for name in missing}
            for future in as_completed(futures):
                print(future.result())

    # if everything is done, write the progress marker
    if not missing and listofblobs and blob_name_injected:
        db.create_schema_and_indexes()
        value_to_insert = "DATAINGESTCOMPLETE"
        stmt = (
            insert(db.tables[progress_table_name])
            .values(status_text=value_to_insert)
            .on_conflict_do_nothing()
        )
        with db.conn_tx() as conn:
            conn.execute(stmt)

    return True

