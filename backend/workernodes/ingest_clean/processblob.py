
from sqlalchemy import Table, Column, MetaData, String, select

from sqlalchemy import text, MetaData, Table, inspect
from sqlalchemy.dialects.postgresql import insert
import hashlib
import os
from .readbuckets import azurebucket

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
table_name_documents = os.environ.get("RAWDATATEXTTABLE")

def row_hash(row):
    row_str = "|".join([str(x) for x in row])
    return hashlib.md5(row_str.encode()).hexdigest()


def injectintoDB(db, rows_to_insert):

    db.insert_into_table(
        table_name=table_name_documents,
        rows=rows_to_insert,
        conflict_key="row_hash",
        do_update=False,
        autoLoad=True,
    batch_size=500
)

def flatten_list_of_dicts(data):
    result = []

    def _flatten(item):
        if isinstance(item, dict):
            result.append(item)
        elif isinstance(item, list):
            for x in item:
                _flatten(x)
        # ignore other types (str, int, etc.)

    _flatten(data)
    return result
        
def process_and_store(db, de, container_client, blob_name):
    
    print(blob_name)
    
    blob = azurebucket.getblobbytes(container_client, blob_name)
    
    de.extract_text(blob, blob_name)
    ## results could be nested files of unknown depth and should be flattened
    if isinstance(de.results, list):
        results_flat = flatten_list_of_dicts(de.results)
        
        ## add row_hash as a dict key
        for items in results_flat:
            items['row_hash'] = row_hash([items for _, items in items.items()])
            items['blob_name'] = blob_name
        
    elif isinstance(de.results, dict): results_flat = [de.results]    
    injectintoDB(db, results_flat)
    
    # insert results into DB here...
    return f"Inserted {len(results_flat)} docs"
    