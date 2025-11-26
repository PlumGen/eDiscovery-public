
from sqlalchemy import text, inspect, select
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import os
import json
from sqlalchemy import Table, Column, String, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
import numpy as np
from .EmbedThread_GPU import main
from .standardizeEmbed import standardizeEmbed
import torch
import os
import embedizelocal.taskManager as taskManager

from .errors import EmbeddingError, EmbeddingOOMError

import multiprocessing as mp

def run_main_in_subprocess(args):
    return main(*args)

    
    
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)  

table_name_tokenize = os.environ.get("TOKENIZEDATATEXTTABLE") 
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
embed_tokencount_thresh = int(os.environ.get("EMBEDTOKENCOUNTTHRESHOLD"))




def main_embed(db, gpu_available):
    print('Testing Testing Embed Init')  
   
    engine = db.get_engine()
    inspector = inspect(engine) 
    progress_table = db.tables[progress_table_name]
    
    
    print('Testing Testing Embed')    
    with db.conn_read() as conn:
        result = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text.like("%TOKENIZECOMPLETE%"))
        ).fetchall()

    tokenizecomplete_list = [r[0].split('TOKENIZECOMPLETE:')[1] for r in result if 'TOKENIZECOMPLETE:' in r[0]]
    
    with db.conn_read() as conn:
        result = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text.like("%EMBEDCOMPLETE%"))
        ).fetchall()

    embedcomplete_list = [r[0].split('EMBEDCOMPLETE:')[1] for r in result if 'EMBEDCOMPLETE:' in r[0]]
    
    embedcomplete_incomplete = [m for m in tokenizecomplete_list if m not in embedcomplete_list]
    
    emebddone = len(embedcomplete_incomplete) == 0    
    embedcomplete_incomplete = [i for i in embedcomplete_incomplete if i!='ALL']
        
    if emebddone and inspector.has_table(table_name_embed):
        print("EMBEDCOMPLETE already exists in progress table.")
    elif tokenizecomplete_list and inspector.has_table(table_name_tokenize):
        print("EMBEDCOMPLETE not found.")
        
        while True:
            nextTask = taskManager.GetNextTask(db)
            if nextTask['model']!='All':
                modelName = nextTask['model']    

                query = f'''
                    SELECT id, row_hash, row_hash_model, num_sentences, tokenized, wordcount, alphanumeric, token_count, model_name
                    FROM {table_name_tokenize}
                    WHERE model_name = '{modelName}' 
                    AND 
                    wordcount > {embed_tokencount_thresh}
                    {'' if not inspector.has_table(table_name_embed) else f"AND row_hash_model NOT IN (SELECT row_hash_model FROM {table_name_embed} WHERE model_name = '{modelName}')"}
                '''

                
                    
                # Process embedding in chunks
                safeEmbedChunkDetermined=False
                currentMultiple=1
                for model_df in db.resilient_read_query_keyset(query, chunksize=chunksize): # db.resilient_read_query_keyset(query, chunksize=chunksize):
                    if model_df.empty:
                        continue
                    

                    lock_key = f"{nextTask['Process']}:{modelName}"
                    abletoRenewLock = taskManager.renew_lock(db, lock_key)
                    if not abletoRenewLock: break
                
                    if len(set(model_df.model_name)) != 1:
                        raise ValueError("Differing Embed Models Used for this Batch")
                    
                    file = {'column_name': 'tokenized', 'modelname': modelName}
                    
                    if gpu_available.type=='cuda':
                        torch.cuda.empty_cache()
                        torch.cuda.ipc_collect()
                    
                    model_df = model_df.drop(columns='id')
                    
                    if not safeEmbedChunkDetermined:
                        with mp.get_context("spawn").Pool(1) as pool:
                            while True:
                                args = (model_df, file, gpu_available, modelName,
                                        int(currentMultiple * chunksize))

                                try:
                                    df = pool.apply(run_main_in_subprocess, (args,))
                                except EmbeddingOOMError as e:
                                    # specific OOM → shrink batch and retry
                                    torch.cuda.empty_cache()
                                    currentMultiple = max(0.1, currentMultiple * 0.9)
                                    print(f"OOM → reducing batch size to {int(currentMultiple*chunksize)}")
                                    continue
                                except EmbeddingError as e:
                                    # all other embedding errors → stop and bubble up
                                    raise RuntimeError(f"Embedding failed: {e}") from e
                                except Exception as e:
                                    # unexpected errors outside embedding
                                    raise

                                if df is None or "embed" not in df.columns:
                                    raise RuntimeError("Worker returned no data or missing 'embed' column")

                                safeEmbedChunkDetermined = True
                                print(f"✅ Safe embed chunk size: {int(currentMultiple*chunksize)}")
                                break
                                
                    else:            
                        df = main(model_df, file, cudaflag_override=gpu_available, model_name=modelName, batch_size=int(currentMultiple*chunksize)) 
                        
                    if gpu_available.type=='cuda':                        
                        torch.cuda.empty_cache()
                        torch.cuda.ipc_collect()
                    
                    print('out of main function')
                    df.drop(columns='tokenized', inplace=True)
                    rows_to_insert = df.to_dict(orient='records')
                    db.insert_into_table(
                        table_name=table_name_embed,
                        rows=rows_to_insert,
                        conflict_key="row_hash_model", 
                        do_update=False,
                        batch_size=chunksize
                    )
                        

                    print(f"Injected embeddings DataFrame into '{table_name_embed}'.")

            # Compare embed coverage
            textembed_complete=[]
            for  MAINEMBEDMODEL in [i for i in tokenizecomplete_list if i!='ALL']:
                print(MAINEMBEDMODEL)
                with db.conn_read() as conn:
                    result = conn.execute(text(f"SELECT COUNT(DISTINCT row_hash_model) FROM {table_name_embed} WHERE model_name = '{MAINEMBEDMODEL}'"))
                    unique_count = result.scalar()

                with db.conn_read() as conn:
                    result = conn.execute(text(f"""SELECT COUNT(DISTINCT row_hash_model) FROM {table_name_tokenize} 
                                                WHERE model_name = '{MAINEMBEDMODEL}'
                                                AND
                                                wordcount > :thresh"""), {"thresh": embed_tokencount_thresh})
                    row_count_cleantext = result.scalar()  # Gets the first column of the first row
                
                
                    print(f"Number of rows in {table_name_tokenize}: {row_count_cleantext}")
                    print(f"Number of unique row_hash_model in {table_name_embed}: {unique_count}")

                if (row_count_cleantext == unique_count):
                    textembed_complete.append(MAINEMBEDMODEL)
                    taskManager.markDone(db, nextTask['Process'], MAINEMBEDMODEL)
                    
            if 'ALL' in tokenizecomplete_list:
                if len([i for i in tokenizecomplete_list if i!='ALL'])==len(textembed_complete):
                    textembed_complete.append('ALL')
                    taskManager.markDone(db, nextTask['Process'], 'All')        
            
            for MAINEMBEDMODEL in textembed_complete:

                    
                value_to_insert = f"EMBEDCOMPLETE:{MAINEMBEDMODEL}"
                stmt = insert(progress_table).values(status_text=value_to_insert).on_conflict_do_nothing()
                with db.conn_tx() as conn:
                    conn.execute(stmt)
                print(f'embed marked stage as complete for model {MAINEMBEDMODEL}')   
                
            if nextTask['model']=='All':
                return True   

    return True