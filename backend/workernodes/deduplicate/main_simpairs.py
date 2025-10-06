
from sqlalchemy import Column 
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, text, MetaData, Table, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError


import pandas as pd
import numpy as np
import os
import hashlib
from tqdm import tqdm

import json
import faiss
import torch

def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

def row_hash(row):
    row_str = "|".join([str(x) for x in row])
    return hashlib.md5(row_str.encode()).hexdigest() 

def save_similarity_pairs_to_sql(df_all, source_indices, distances, query_indices):
    rows = []
    row_hash_arr = df_all.row_hash.values
    row_hash_model_arr = df_all.row_hash_model.values
    num_sentences_arr = df_all.num_sentences.values

    for local_i, (targets, sims) in enumerate(zip(source_indices, distances)):
        source_idx = query_indices[local_i]
        for target_idx, sim in zip(targets, sims):
            if source_idx == target_idx:
                continue  # self match

            if row_hash_arr[source_idx] == row_hash_arr[target_idx]:
                continue  # true duplicate

            if source_idx > target_idx:
                continue  # symmetrical duplicate

            rows.append({
                'source_idx': source_idx,
                'target_idx': target_idx,
                'similarity': float(sim),
                'source_row_hash_model': row_hash_model_arr[source_idx],
                'target_row_hash_model': row_hash_model_arr[target_idx],
                'source_row_hash': row_hash_arr[source_idx],
                'target_row_hash': row_hash_arr[target_idx],                
                'source_num_sentence': num_sentences_arr[source_idx],
                'target_num_sentence': num_sentences_arr[target_idx],
            })
    return pd.DataFrame(rows)

def build_faiss_index(embeddings, use_ivf=True, nlist=100, normalize=False):
    d = embeddings.shape[1]

    if normalize:
        faiss.normalize_L2(embeddings)

    if use_ivf and len(embeddings) >= nlist:
        quantizer = faiss.IndexFlatIP(d)
        index = faiss.IndexIVFFlat(quantizer, d, nlist)
        index.train(embeddings)
        index.add(embeddings)
        print(f"Using IndexIVFFlat with nlist={nlist}")
    else:
        # index = faiss.IndexFlatIP(d)
        

        # Create a FlatIP index on GPU
        index_cpu = faiss.IndexFlatIP(d)
        
        if get_device() == 'cuda':
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # 0 = GPU id
        else: index= index_cpu
                   
        index.add(embeddings)
        print("Using IndexFlatIP (fallback)")

    return index
 

def safe_faiss_block_search(index, embeddings, start, block_size, normalize=False):
    N = embeddings.shape[0]


    end = min(N, start + block_size)
    query_block = embeddings[start:end]

    if normalize:
        faiss.normalize_L2(query_block)

    k = min(block_size, index.ntotal)
    if not index.is_trained and isinstance(index, faiss.IndexIVFFlat):
        raise RuntimeError("IndexIVFFlat was not trained!")

    print('starting index search')
    D, I = index.search(query_block, k=k)
    return (D, I, np.arange(start, end))

    
if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_similaritypairs = os.environ.get("SIMPAIRSDATATEXTTABLE")

progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))


embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))

## correction for this module
block_size=int(block_size/4)

mainEmbedModel = str(os.environ.get("MAINEMBEDMODEL"))



def main_simpairs(db): 
    engine = db.get_engine()
    inspector = inspect(engine)
    # Check and create the table if it doesn't exist

    progress_table = db.metadata.tables[progress_table_name]  
                  
                            
    with engine.connect() as conn:
        embeddone = conn.execute(select(progress_table.c.status_text).where(progress_table.c.status_text == f"EMBEDCOMPLETE:{mainEmbedModel}")).first()      

    with engine.connect() as conn:
        simpairsdone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "SIMPAIRSCOMPLETE")
        ).first() 
            
        
    if simpairsdone and inspector.has_table(table_name_similaritypairs):
        print("SIMPAIRSCOMPLETE already exists in progress table.")
    elif embeddone and inspector.has_table(table_name_embed):
        print("SIMPAIRSCOMPLETE not found.")
        
        
        query = text(f"SELECT id, row_hash, row_hash_model, embed, num_sentences FROM {table_name_embed} WHERE model_name = '{mainEmbedModel}'")

        listofDfs = []
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):listofDfs.append(df)
            
        df = pd.concat(listofDfs)
        df = df.sort_values(by='num_sentences', ascending=False)
        df = df.reset_index(drop=True)
        df = df.drop(columns='id')
            
        print(f"Building FAISS Index")
        embeddings = np.vstack(df[embed_col].values).astype('float32')
        faiss.normalize_L2(embeddings)
        
        assert not np.isnan(embeddings).any(), "NaNs in embeddings"
        assert not np.isinf(embeddings).any(), "Inf in embeddings"
        assert np.linalg.norm(embeddings, axis=1).min() > 0, "Zero vectors found"


        nlist = min(100, max(1, len(embeddings) // 20))
        
        index = build_faiss_index(embeddings, use_ivf=False, nlist=nlist)
        N = embeddings.shape[0]
        print(f"Search through blocks of: {block_size} block size")
        seen_hashes = set()
        for start in tqdm(range(0, N, block_size)):
            D, I, query_indices = safe_faiss_block_search(index, embeddings, start, block_size=block_size)
            chunked_df = save_similarity_pairs_to_sql(df, I, D, query_indices)
            seen_hashes.update(chunked_df['source_row_hash'])
            seen_hashes.update(chunked_df['target_row_hash'])
                        
            chunked_df['row_hash_tablespec'] = pd.util.hash_pandas_object(chunked_df.astype(str), index=False).astype(str)

            chunked_df['model_name'] = mainEmbedModel

            print('chunked_df.shape[0]')
            print(chunked_df.shape[0])
            
            rows_to_insert = chunked_df.to_dict(orient='records')
            db.insert_into_table(
                table_name=table_name_similaritypairs,
                rows=rows_to_insert,
                conflict_key="row_hash_tablespec", 
                do_update=False,
                batch_size=500
            )

            print(f"Injected similarity pairs DataFrame into '{table_name_similaritypairs}'.")
                        
            

        unique_count=len(seen_hashes)
        faispairs_complete=False
        with engine.connect() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(DISTINCT row_hash) FROM (
                    SELECT source_row_hash AS row_hash FROM {table_name_similaritypairs}
                    UNION
                    SELECT target_row_hash AS row_hash FROM {table_name_similaritypairs}
                ) AS flat
            """))
            row_count_rawtext = result.scalar()

            
            
            print(f"Number of unique in {table_name_similaritypairs}: {row_count_rawtext}")
            print(f"Number of unique hashes processed in this module: {unique_count}")

            faispairs_complete = row_count_rawtext == unique_count
            

        if faispairs_complete:
            # Load the table
            

            # Insert a new unique status value
            value_to_insert = "SIMPAIRSCOMPLETE"

            
            stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()

            with engine.begin() as conn:
                conn.execute(stmt)
                
            print('marked stage as complete')   
            
    else:
        print('Something is wrong as the initial checks are not returning expected results')
    return True