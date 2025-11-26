
from sqlalchemy import Table, Column, MetaData, String, select

from sqlalchemy import create_engine, text, MetaData, Table, inspect
from sqlalchemy.dialects.postgresql import insert

import pandas as pd

import os
import hashlib
from sqlalchemy import inspect, text
from .tokenizeParallel import tokenize_chunked_df

from sqlalchemy import inspect, MetaData, Table, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.dialects.postgresql import insert
import json


def row_hash(row):
    row_str = "|".join([str(x) for x in row])
    return hashlib.md5(row_str.encode()).hexdigest()


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
BUCKETNAME = os.environ.get("BUCKETNAME")
table_name_tokenize = os.environ.get("TOKENIZEDATATEXTTABLE")
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
table_name_cleantext = os.environ.get("CLEANEDDATATEXTTABLE")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))


MAINEMBEDMODEL = os.environ.get("MAINEMBEDMODEL")

def main_tokenizetext(db, embedding_models):

    engine = db.get_engine()
    inspector = inspect(engine)
    # Check and create the table if it doesn't exist

    progress_table = db.metadata.tables[progress_table_name]   
    with db.conn_read() as conn:
        result = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text.like("%TOKENIZECOMPLETE%"))
        ).fetchall()

    tokenizecomplete_list = [r[0].split('TOKENIZECOMPLETE:')[1] for r in result if 'TOKENIZECOMPLETE:' in r[0]]
    tokenizecomplete_incomplete = [m for m in embedding_models if m not in tokenizecomplete_list]
    tokenizedone = len(tokenizecomplete_incomplete) == 0
   
    print('tokenizedone')
    print(tokenizedone)
    print('inspector.has_table(table_name_tokenize)')
    print(inspector.has_table(table_name_tokenize))
    
    if tokenizedone and inspector.has_table(table_name_tokenize):
        print("TOKENIZECOMPLETE already exists in progress table.")
    else:
        print("TOKENIZECOMPLETE not found.")
        
        for MAINEMBEDMODEL in tokenizecomplete_incomplete:
            inspector = inspect(engine)
            metadata = MetaData()

            # If first time, create table
            if not inspector.has_table(table_name_tokenize):
                query = f'SELECT "id", "clean_text", "docid", "chunkid", "row_hash", num_sentences FROM {table_name_cleantext}'
            else:                
                query = f"""
                    SELECT "id", "clean_text", "docid", "chunkid", row_hash, num_sentences
                    FROM {table_name_cleantext}
                    WHERE row_hash NOT IN (
                        SELECT row_hash FROM {table_name_tokenize} WHERE model_name = '{MAINEMBEDMODEL}'
                    )
                """

            # with engine.connect() as conn:
            for df in db.resilient_read_query_keyset(query, chunksize=chunksize):

                if df.shape[0]>0:
                    df = df.drop(columns='id')
                    
                    df['clean_text'] = df['clean_text'].astype(str)
                    df = tokenize_chunked_df(df, text_col='clean_text', model_name=MAINEMBEDMODEL)

                    df['wordcount'] = df.clean_text.str.split().map(len)
                    df['alphanumeric'] = df.clean_text.apply(lambda x: len([i for i in x.split() if i.isalpha()]) / len(x))
                    df['token_count'] = df.tokenized.apply(lambda x:sum([1 for i in x['input_ids'] if i!=0])-2)
                    df['tokenized'] = df['tokenized'].apply(json.dumps)
                    df['model_name'] = MAINEMBEDMODEL
                    df['row_hash_model'] = df[['row_hash', 'model_name']].apply(row_hash, axis=1)

                    
                    rows_to_insert = df.to_dict(orient='records') 
                    db.insert_into_table(
                        table_name=table_name_tokenize,
                        rows=rows_to_insert,
                        conflict_key="row_hash_model", 
                        do_update=False,
                        batch_size=chunksize
                    )


                    print(f"Injected tokenize into DataFrame into '{table_name_tokenize}'.")

        texttokenize_complete=[]
        for  MAINEMBEDMODEL in embedding_models:
            with db.conn_read() as conn:
                result = conn.execute(text(f"SELECT COUNT(DISTINCT row_hash) FROM {table_name_tokenize} WHERE model_name = '{MAINEMBEDMODEL}'"))
                unique_count = result.scalar()

            
            with db.conn_read() as conn:
                result = conn.execute(text(f"SELECT COUNT(DISTINCT row_hash) FROM {table_name_cleantext}"))
                row_count_cleantext = result.scalar()  # Gets the first column of the first row
            
            
                print(f"Number of rows in {table_name_cleantext}: {row_count_cleantext}")
                print(f"Number of unique row_hash in {table_name_tokenize}: {unique_count}")

            if (row_count_cleantext == unique_count):
                texttokenize_complete.append(MAINEMBEDMODEL)
        

        if len([i for i in embedding_models if i not in texttokenize_complete])==0:
            texttokenize_complete.append('ALL')

        for MAINEMBEDMODEL in texttokenize_complete:
            value_to_insert = f"TOKENIZECOMPLETE:{MAINEMBEDMODEL}"
            stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()
            with db.conn_tx() as conn:
                conn.execute(stmt)
            print(f'tokenize marked stage as complete for model {MAINEMBEDMODEL}')      
                

    return True