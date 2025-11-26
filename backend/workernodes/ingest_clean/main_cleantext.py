
from sqlalchemy import Table, Column, MetaData, String, select

from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.dialects.postgresql import insert

import pandas as pd

import os
import hashlib
from sqlalchemy import inspect, text
from .chunktextsparallel_runner import chunk_documents_parallel


def row_hash(row):
    row_str = "|".join([str(x) for x in row])
    return hashlib.md5(row_str.encode()).hexdigest()


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
BUCKETNAME = os.environ.get("BUCKETNAME")
table_name_rawtext = os.environ.get("RAWDATATEXTTABLE")
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
table_name_cleantext = os.environ.get("CLEANEDDATATEXTTABLE")


UNIQUEROWID = os.environ.get("UNIQUEROWID")
BODYCOLUMNNAME = os.environ.get("BODYCOLUMNNAME")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))

MAINEMBEDMODEL = os.environ.get("MAINEMBEDMODEL")
MAINNLPMODEL = os.environ.get("MAINNLPMODEL")

regex_list=[
    (r"[\r\n]+", " "),
    (r"[^\w@%&$.,:/\-–()]+", " "),       
    (r"\s{2,}", ""),
]

initargs=(MAINEMBEDMODEL, MAINNLPMODEL)


def main_cleantext(db, numrounds=2, thisround=1):

    engine = db.get_engine()
    inspector = inspect(engine)
    # Check and create the table if it doesn't exist

    progress_table = db.metadata.tables[progress_table_name]
        
    with db.conn_read() as conn:
        dataingest = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "DATAINGESTCOMPLETE")
        ).first()

    with db.conn_read() as conn:
        textclean = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "TEXTCLEANCOMPLETE")
        ).first()
        
        
        
    if textclean and inspector.has_table(table_name_cleantext):
        print("TEXTCLEANCOMPLETE already exists in progress table.")
    elif dataingest:
        print("TEXTCLEANCOMPLETE not found.")
        
        if BODYCOLUMNNAME=='NONE':
            # Step 1: Get text-like columns
            columns = inspect(engine).get_columns(table_name_rawtext)
            text_cols = [col["name"] for col in columns if col["type"].__class__.__name__.lower() in {"text", "string", "varchar"}]

            # Step 2: Build query with quoted aliases
            char_sum_exprs = ", ".join([f'SUM(CHAR_LENGTH("{col}")) AS "{col}"' for col in text_cols])
            sql = f'SELECT {char_sum_exprs} FROM {table_name_rawtext}'

            # Step 3: Run and analyze
            with db.conn_read() as conn:
                result = conn.execute(text(sql)).mappings().first()

            Body = max(result.items(), key=lambda item: item[1] or 0)
            print(f"Column with most total characters: {Body[0]} ({Body[1]})")
            Body = Body[0]
        else:Body = BODYCOLUMNNAME


        if UNIQUEROWID=='NONE':
            docid='row_hash'
            


        columnaNames = {'docid':'docid',
                        'Body':Body}

        
        inspector = inspect(engine)
        metadata = MetaData()

        # If first time, create table
        if not inspector.has_table(table_name_cleantext):
            query = text(f'SELECT id, "{Body}", "{docid}" FROM {table_name_rawtext}')
        else:                
            query = text(f"""
                SELECT id, "{Body}", "{docid}"
                FROM {table_name_rawtext}
                WHERE row_hash NOT IN (
                    SELECT docid FROM {table_name_cleantext}
                )
            """)
            
        dfs = []
        ignored_docids = 0
        # with engine.connect() as conn:
        for chunk in db.resilient_read_query_keyset(query, chunksize=chunksize):
            df = chunk.rename(columns={docid: 'docid'})
            # Optional: process chunk here before storing

            rows = df[['docid', Body]].to_dict(orient='records')
            print(f'Documents downloaded this round: {df.shape[0]}')
            
            chunked_df =  chunk_documents_parallel(rows, chunk_size=500, overlap=0, processes=None, regex_list=regex_list, baselineModels=initargs, columnaNames=columnaNames)
            chunked_df['row_hash'] = chunked_df.apply(row_hash, axis=1)
            chunked_df = chunked_df.drop_duplicates(subset=['row_hash'])


            print(f'Documents uploading this round: {chunked_df.shape[0]}')
            
            ignored_docids += (df.shape[0] - chunked_df.shape[0])
            
            rows_to_insert = chunked_df.to_dict(orient='records')

            db.insert_into_table(
                table_name=table_name_cleantext,
                rows=rows_to_insert,
                conflict_key="row_hash",
                do_update=False,
                batch_size=chunksize
            )
            print(f"Injected cleaned text DataFrame into '{table_name_cleantext}'.")


        with db.conn_read() as conn:
            result = conn.execute(text(f"SELECT COUNT(DISTINCT docid) FROM {table_name_cleantext}"))
            unique_count = result.scalar()

        textcleaning_complete=False
        with db.conn_read() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name_rawtext}"))
            row_count_rawtext = result.scalar()  # Gets the first column of the first row
            
            
            print(f"Number of rows in {table_name_rawtext}: {row_count_rawtext}")
            print(f"Number of unique docid in {table_name_cleantext}: {unique_count}")
            print(f"Number of ignored docid in {table_name_cleantext}: {ignored_docids}")
            
            textcleaning_complete = row_count_rawtext == unique_count+ignored_docids
            print(f"Is text cleaning complete? {textcleaning_complete}")


        if textcleaning_complete:
            # Load the table
            

            # Insert a new unique status value
            value_to_insert = "TEXTCLEANCOMPLETE"
 
            stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()

            with db.conn_tx() as conn:
                conn.execute(stmt)
                
            print('marked stage as complete')        

        elif thisround<numrounds:       
            print('Not all documents cleaned yet, doing another round.')
            main_cleantext(db, numrounds=numrounds, thisround=thisround+1)

                

    return True