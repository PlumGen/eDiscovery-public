
from sqlalchemy import Column 
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, text, MetaData, Table, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError


import pandas as pd
import numpy as np
import os
import hashlib


import json
import faiss


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    

table_name_similaritypairs = os.environ.get("SIMPAIRSDATATEXTTABLE")
table_name_markedduplicates = os.environ.get("MARKEDDUPLICATESTEXTTABLE")

progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))


embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))


def main_markedduplicates(db):                
    engine = db.get_engine()
    inspector = inspect(engine)
    # Check and create the table if it doesn't exist

    progress_table = db.metadata.tables[progress_table_name]  
        
    # Check and create the table if it doesn't exist

                        
    with db.conn_read() as conn:
        duplicatedefinition = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text.like("%DUPLICATEDEFINITION%"))
        ).first()

    with db.conn_read() as conn:
        simpairsdone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "SIMPAIRSCOMPLETE")
        ).first() 

    with db.conn_read() as conn:
        duplicatesMarked = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "DUPLICATESMARKEDCOMPLETE")
        ).first() 
                
        
    if duplicatesMarked and inspector.has_table(table_name_markedduplicates):
        print("DUPLICATES MARKED already exists in progress table.")
    elif simpairsdone and inspector.has_table(table_name_similaritypairs) and len(duplicatedefinition)>0:
        print("DUPLICATES MARKED not found.")
        
        
        
        similarity_threshold = float(duplicatedefinition[0].split(':')[1])

        query = text(f'SELECT * FROM {table_name_similaritypairs} where similarity>={similarity_threshold}')

        listofDfs = []

        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):listofDfs.append(df)
            
        df = pd.concat(listofDfs)

        source_dict = df.set_index('source_idx')['source_num_sentence'].to_dict()
        target_dict = df.set_index('target_idx')['target_num_sentence'].to_dict()
        num_sentence = {**source_dict, **target_dict}




        N = max(df.source_idx.max(), df.target_idx.max())+1
        visited = np.zeros(N, dtype=bool)
        master_map = {}

        # Pre-group all neighbors per node
        neighbor_map = {}
        for _, row in df.iterrows():
            src, tgt, sim = int(row['source_idx']), int(row['target_idx']), row['similarity']
            if src not in neighbor_map:
                neighbor_map[src] = []
            neighbor_map[src].append((tgt, sim))

        for node in list(num_sentence.keys()):
            if visited[node]:
                continue
            candidates = neighbor_map.get(node, [])
            direct_children = [j for j, sim in candidates if sim >= similarity_threshold and not visited[j]]

            # Choose master: this node (by default), unless child is longer
            all_candidates = [node] + direct_children
            master = max(all_candidates, key=lambda idx: num_sentence[idx])

            master_map[master] = []

            for j in all_candidates:
                if j == master:
                    continue
                master_map[master].append(j)
                visited[j] = True

            visited[master] = True

        # Convert to DataFrame
        records = []
        for master, children in master_map.items():
            records.append((master, master, 'master'))
            for child in children:
                records.append((child, master, 'child'))

        tracking_df = pd.DataFrame(records, columns=['node_id', 'master_id', 'role'])


        source_dict = df.set_index('source_idx')['source_row_hash'].to_dict()
        target_dict = df.set_index('target_idx')['target_row_hash'].to_dict()
        row_hash_dict = {**source_dict, **target_dict}

        source_dict_model = df.set_index('source_idx')['source_row_hash_model'].to_dict()
        target_dict_model = df.set_index('target_idx')['target_row_hash_model'].to_dict()
        row_hash_dict_model = {**source_dict_model, **target_dict_model}
        
        tracking_df['row_hash_model'] = tracking_df.node_id.map(row_hash_dict_model)
        tracking_df['row_hash_model_master'] = tracking_df.master_id.map(row_hash_dict_model)
        
        tracking_df['row_hash'] = tracking_df.node_id.map(row_hash_dict)
        tracking_df['row_hash_master'] = tracking_df.master_id.map(row_hash_dict)
        
        tracking_df = tracking_df[['role', 'row_hash', 'row_hash_master', 'row_hash_model', 'row_hash_model_master']]


        rows_to_insert = tracking_df.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name_markedduplicates,
            rows=rows_to_insert,
#            conflict_key="row_hash", 
            do_update=False,
            batch_size=500
        )
        
        print(f"Injected deduplicated DataFrame into '{table_name_markedduplicates}'.")
        
            
            
            
        with db.conn_read() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(DISTINCT row_hash) FROM (
                    SELECT source_row_hash AS row_hash FROM {table_name_similaritypairs} WHERE similarity>={similarity_threshold}
                    UNION
                    SELECT target_row_hash AS row_hash FROM {table_name_similaritypairs} WHERE similarity>={similarity_threshold}
                ) AS flat
            """))
            row_count_simpairs = result.scalar()
            
            
            
        with db.conn_read() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(DISTINCT row_hash) FROM (
                    SELECT row_hash AS row_hash FROM {table_name_markedduplicates}
                    UNION
                    SELECT row_hash_master AS row_hash FROM {table_name_markedduplicates}
                ) AS flat
            """))
            row_count_marked = result.scalar()
            
            
        print(f"Number of rows that meet threshold in {table_name_similaritypairs}: {row_count_simpairs}")
        print(f"Number of rows in {table_name_markedduplicates}: {row_count_marked}")

        faispairs_complete = row_count_simpairs == row_count_marked

        if faispairs_complete:
            # Load the table
            # Insert a new unique status value
            value_to_insert = "DUPLICATESMARKEDCOMPLETE"

            stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()

            with db.conn_tx() as conn:
                conn.execute(stmt)
                
            print('marked mark duplicates as complete')   
                
    return True                
                                        