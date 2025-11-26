from sqlalchemy import Column 
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, text, MetaData, Table, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError
from collections import Counter

import pandas as pd
import numpy as np
import os
import hashlib
from tqdm import tqdm
import torch
 
import json
import faiss

def row_hash(row):
    row_str = "|".join([str(x) for x in row])
    return hashlib.md5(row_str.encode()).hexdigest()

def save_similarity_pairs_to_sql(df_all, source_indices, distances, query_indices):
    rows = []
    row_hash_model_arr = df_all.row_hash_model.values
    row_hash_arr = df_all.row_hash.values

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

                'similarity': float(sim),
                'source_row_hash': row_hash_arr[source_idx],
                'target_row_hash': row_hash_arr[target_idx],
                'source_row_hash_model': row_hash_model_arr[source_idx],
                'target_row_hash_model': row_hash_model_arr[target_idx],                
                'source_user_label': None,
                'target_user_label': None,
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
#        
        # Create a FlatIP index on GPU
        index_cpu = faiss.IndexFlatIP(d)
        if torch.cuda.is_available():
            res = faiss.StandardGpuResources()
            index = faiss.index_cpu_to_gpu(res, 0, index_cpu)  # 0 = GPU id
        else:index = index_cpu
        
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
    
table_name_rank = os.environ.get("RANKINGDATATEXTTABLE")
table_name_cluster = os.environ.get("CLUSTERINGDATATEXTTABLE")
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_labelcandidates = os.environ.get("LABELCANDIDATESTABLE")
table_name_labelcandidates_validation = os.environ.get("LABELCANDIDATESVALIDATIONTABLE")

progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))

embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))
labelselectionrankquantile=float(os.environ.get("LABELSELECTIONRANKQUANTILE"))

labelselectionvalidationquantile=float(os.environ.get("LABELSELECTIONVALIDATION"))

ENABLELABELCHECK = os.getenv('ENABLELABELCHECK')


def main_candidatelabels(db):
    # get embed, clusters, ranks
    engine = db.get_engine()
    progress_table = db.tables[progress_table_name]
    inspector = inspect(engine)
        
    with db.conn_read() as conn:
        embeddone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "EMBEDCOMPLETE:ALL")
        ).first()      

    with db.conn_read() as conn:
        clusterdone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "CLUSTERCOMPLETE:ALL")
        ).first() 

    with db.conn_read() as conn:
        labelcandidatedone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "LABELCANDIDATECOMPLETE")
        ).first() 

    with db.conn_read() as conn:
        rankingdone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "RANKINGCOMPLETE")
        ).first() 
                    
        
    if labelcandidatedone and inspector.has_table(table_name_labelcandidates):
        print("LABELCANDIDATECOMPLETE already exists in progress table.")
    elif embeddone and inspector.has_table(table_name_embed) and clusterdone and inspector.has_table(table_name_cluster) and rankingdone and inspector.has_table(table_name_rank):
        print("LABELCANDIDATECOMPLETE not found, in main function.")
        
        
        
        ## get embed, rank, clustering, then identify candidate labels, then do a sim calculation so that the user can be notified of possible errors
        query = f"""SELECT *
        FROM {table_name_rank}
        """

        list_rank_df=[]
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):list_rank_df.append(df)
        rank_df = pd.concat(list_rank_df)

        query = f"""SELECT *
        FROM {table_name_cluster}
        """
        list_cluster_df=[]
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):list_cluster_df.append(df)
        cluster_df = pd.concat(list_cluster_df)

        rank_df = rank_df.drop(columns='id')
        cluster_df = cluster_df.drop(columns='id')
        
        combined_df = rank_df.merge(cluster_df, how='inner', on=['row_hash', 'row_hash_model'])
        combined_df = combined_df.dropna()


        columnsList_Base = ['leiden', 'louvain', 'spectral_max', 'spectral_balanced', 'hdbscan']
        labelCandidates_df_combineAllResults = []    
        for thismodelName in set(combined_df.model_name_x):
            thisModel_combined_df = combined_df[combined_df.model_name_x==thismodelName]
            thisModel_combined_df = thisModel_combined_df.sort_values(by='Selection_Rank_Deterministic')
            thisModel_combined_df.reset_index(drop=True, inplace=True)
            windowsSize_local = thisModel_combined_df[thisModel_combined_df.Selection_Distance>=thisModel_combined_df.Selection_Distance.quantile(labelselectionrankquantile)].index[0]
            
            print(f'Determined Window Size for model<{thismodelName}>: {windowsSize_local}')


            collect_dfs_df = {}
            for approach in ['balanced', 'stratified']:
                collect_dfs = []
                for col in columnsList_Base:
                    col_classes = list(set(thisModel_combined_df[col]))

                    if approach == 'balanced':
                        per_class = int(windowsSize_local/len(columnsList_Base) / len(col_classes))
                        for class_label in col_classes:
                            collect_dfs.append(thisModel_combined_df[thisModel_combined_df[col] == class_label].head(per_class))

                    elif approach == 'stratified':
                        total = thisModel_combined_df.shape[0]
                        freqs = Counter(thisModel_combined_df[col])
                        for class_label in col_classes:
                            ratio = freqs[class_label] / total
                            n_samples = int(np.floor(ratio * windowsSize_local))
                            collect_dfs.append(thisModel_combined_df[thisModel_combined_df[col] == class_label].head(n_samples))

                collect_dfs_df[approach] = pd.concat(collect_dfs).drop_duplicates(subset='row_hash_model')
            labelCandidates_df = pd.concat([values for key, values in collect_dfs_df.items()])
            labelCandidates_df = labelCandidates_df.drop_duplicates(subset='row_hash_model')
            labelCandidates_df_combineAllResults.append(labelCandidates_df[:windowsSize_local])

        labelCandidates_df_combineAllResults_df = pd.concat(labelCandidates_df_combineAllResults).drop_duplicates(subset='row_hash')
        labelCandidates_df_combineAllResults_df = labelCandidates_df_combineAllResults_df.sort_values(by='Selection_Rank_Deterministic')
        labelCandidates_df_combineAllResults_df = labelCandidates_df_combineAllResults_df.reset_index(drop=True)
        labelCandidates_df_combineAllResults_df['id'] = labelCandidates_df_combineAllResults_df.index+1
        labelCandidates_df_combineAllResults_df=labelCandidates_df_combineAllResults_df[['id', 'row_hash', 'row_hash_model']]


        
        rows_to_insert = labelCandidates_df_combineAllResults_df.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name_labelcandidates,
            rows=rows_to_insert,
            conflict_key="row_hash",
            do_update=False,
            batch_size=500
        )
        
        print(f"Injected label candidates DataFrame into '{table_name_labelcandidates}'.")


                
        query = f"""SELECT id, row_hash
        FROM {table_name_labelcandidates}
        """

        list_candidate_hash=[]
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):list_candidate_hash.append(df)
        list_candidate_hash = pd.concat(list_candidate_hash)


        candidatelabelnodesidentified=False
        print('Length Checks')
        print(len(set(list_candidate_hash.row_hash)^set(labelCandidates_df_combineAllResults_df.row_hash)))
        


        if len(set(list_candidate_hash.row_hash)^set(labelCandidates_df_combineAllResults_df.row_hash))==0:
            candidatelabelnodesidentified=True
            
        if candidatelabelnodesidentified:
            # Load the table

            # Insert a new unique status value
            value_to_insert = "LABELCANDIDATECOMPLETE"

            
            stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()

            with db.conn_tx() as conn:
                conn.execute(stmt)
                
            print('marked stage as complete')  
            
            if ENABLELABELCHECK=='TRUE':
                db.createTriggerfunctions()           
            
            
    return True                