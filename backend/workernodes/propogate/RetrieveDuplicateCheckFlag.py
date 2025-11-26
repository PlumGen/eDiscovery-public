import os
import pandas as pd
from sqlalchemy import text

table_name__propogation_progress  = os.environ.get("PROPOGATIONPROGRESS")
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_deduplicates     = os.environ.get("MARKEDDUPLICATESTEXTTABLE")

def RetrieveDuplicateCheckFlag(db):
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__propogation_progress}"), conn)


    duplicateListIDs = None
    if 'DuplicateSanityCheck' in set(set().union(*status_df.additionalops.dropna())):

        query_entire = f"""
            SELECT row_hash, row_hash_master
            FROM {table_name_deduplicates}
            WHERE role='child'
        """
        with db.conn_read() as conn:
            result = conn.execute(text(query_entire))
            duplicates_df = pd.DataFrame(result.fetchall(), columns=result.keys())
            

        duplicateListIDs = duplicates_df
    return duplicateListIDs