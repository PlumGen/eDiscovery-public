
from sqlalchemy import Column 
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, text, MetaData, Table, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError


import pandas as pd
import numpy as np
import os

from .originalClusteringGPU import runClustering



if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_cluster = os.environ.get("CLUSTERINGDATATEXTTABLE")


progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))

embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))


def main_cluster(db, RunCheck):
   
               
    engine = db.get_engine()
    progress_table = db.tables[progress_table_name]
    inspector = inspect(engine)

                   
  
    with db.conn_read() as conn:
        result = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text.like("%EMBEDCOMPLETE%"))
        ).fetchall()

    embedcomplete_list = [r[0].split('EMBEDCOMPLETE:')[1] for r in result if 'EMBEDCOMPLETE:' in r[0]]
    
    with db.conn_read() as conn:
        result = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text.like("%CLUSTERCOMPLETE%"))
        ).fetchall()

    clustercomplete_list = [r[0].split('CLUSTERCOMPLETE:')[1] for r in result if 'CLUSTERCOMPLETE:' in r[0]]
    
    clustercomplete_incomplete = [m for m in embedcomplete_list if m not in clustercomplete_list]
    
    clusterddone = len(clustercomplete_incomplete) == 0    
    clustercomplete_incomplete = [i for i in clustercomplete_incomplete if i!='ALL']
            
         
    if clusterddone and inspector.has_table(table_name_cluster):
        print("CLUSTERCOMPLETE already exists in progress table.")
    elif embedcomplete_list and inspector.has_table(table_name_embed):
        print("CLUSTERCOMPLETE not found.")
        
        for embed_model in clustercomplete_incomplete:
            
            query = f"SELECT id, row_hash, row_hash_model, model_name, embed FROM {table_name_embed} WHERE model_name = '{embed_model}'"
            listofDfs = []
            # with engine.connect() as conn:
            for df in db.resilient_read_query_keyset(query, chunksize=chunksize):listofDfs.append(df)
            
            if not listofDfs:continue
            df = pd.concat(listofDfs)
            df = df.reset_index(drop=True)


            df = runClustering(df, RunCheck, numberoflegalissues = 16)
            df = df[['row_hash', 'row_hash_model', 'model_name', 'spectral_max', 'spectral_balanced', 'louvain', 'leiden', 'hdbscan', 'hdbscan_fix']]

            rows_to_insert = df.to_dict(orient='records')
            db.insert_into_table(
                table_name=table_name_cluster,
                rows=rows_to_insert,
                conflict_key="row_hash_model",
                do_update=False,
                batch_size=500
            )

            print(f"Injected clusters DataFrame into '{table_name_cluster}'.")

        getCompleted_clusters = []
        for embed_model in embedcomplete_list:
            with db.conn_read() as conn:
                result = conn.execute(text(f"SELECT COUNT(DISTINCT row_hash_model) FROM {table_name_embed} WHERE model_name = '{embed_model}'"))
                unique_count = result.scalar()

            texttokenize_complete=False
            with db.conn_read() as conn:
                result = conn.execute(text(f"SELECT COUNT(DISTINCT row_hash_model) FROM {table_name_cluster} WHERE model_name = '{embed_model}'"))
                row_count_cluster = result.scalar()  # Gets the first column of the first row
                
                
                print(f"Number of rows in {table_name_embed}: {unique_count}")
                print(f"Number of rows in {table_name_cluster}: {row_count_cluster}")

                texttokenize_complete = row_count_cluster == unique_count
                if texttokenize_complete:
                    getCompleted_clusters.append(embed_model)
        
        if len([i for i in embedcomplete_list if i!='ALL'])==len(getCompleted_clusters):
            getCompleted_clusters.append('ALL')

        for model_embed in getCompleted_clusters:
            # Load the table
            

            # Insert a new unique status value
            value_to_insert = f"CLUSTERCOMPLETE:{model_embed}"

            
            stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()

            with db.conn_tx() as conn:
                conn.execute(stmt)
                
            print(f'clustering marked stage as complete for model {model_embed}')        
            
            
        return True