import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd
warnings.filterwarnings("ignore", message="A value is trying to be set on a copy")



import torch
computeHardware = 'CPU'
if torch.cuda.is_available():
    computeHardware = 'GPU'
    

from sqlalchemy import text 

import pandas as pd
import numpy as np
import os
import time 
from .PlumGen_ORCA import PlumGen_ORCA

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    

table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_rankingtable = os.environ.get("RANKINGDATATEXTTABLE")

progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))

embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))

rawtextdata   = os.environ.get("RAWDATATEXTTABLE")
cleantextdata = os.environ.get("CLEANEDDATATEXTTABLE")
table_name_tokenize  = os.environ.get("TOKENIZEDATATEXTTABLE")

table_name_cluster = os.environ.get("CLUSTERINGDATATEXTTABLE")
table_name_prepropogationtable = os.environ.get("PREPROPOGATEDLABELS")
table_name_reverseprepropogationtable = os.environ.get("REVERSEPREPROPOGATEDLABELS")


def getLabeledNodes(db=None, table_name_masterLabels=table_name_masterLabels):

    subquery = f"""
    SELECT id
    FROM (
        SELECT id, row_hash, confidence,
            ROW_NUMBER() OVER (PARTITION BY row_hash ORDER BY confidence DESC, id) AS rank
        FROM {table_name_masterLabels}
    ) sub
    WHERE rank = 1
    """

    query = f"""
    SELECT *
    FROM {table_name_masterLabels}
    WHERE id IN ({subquery})
    """

    list_rank_df = []
    for df in db.resilient_read_query_keyset(query, key_column='id', chunksize=chunksize):
        list_rank_df.append(df)
    Master_df = pd.concat(list_rank_df)
    
    Master_df = Master_df.rename(columns={'label':'user_label_actual'})
    Master_df['user_label_standard'] = Master_df['user_label_actual']
    
    return Master_df

def getRankingTable(db):
    
    query = f'SELECT * FROM {table_name_rankingtable}'

    listofDfs = []
    # with engine.connect() as conn:
    for df in db.resilient_read_query_keyset(query, chunksize=chunksize):listofDfs.append(df)

        ### the rest of the code below could be run under this loop if the nodes are too large
    df = pd.concat(listofDfs)
    df = df.reset_index(drop=True)

    df_Save=df.copy()
        
    query = text(f"""
        SELECT row_hash_model, row_hash FROM {table_name_tokenize}
        WHERE  row_hash_model IN :hashes
    """)

    with db.conn_read() as conn:
        row_hash_map1 = pd.read_sql_query(query, conn, params={"hashes": tuple(df_Save.row_hash_model.values)})
    
    row_hash_map1 = dict(zip(row_hash_map1.row_hash_model, row_hash_map1.row_hash))     
    df_Save['row_hash'] = df_Save.row_hash_model.map(row_hash_map1)   
    
    df_Save = df_Save.drop(columns = 'row_hash_model')
    
    return  df_Save
               

def getRelevantEmbeds(df_Save, db=None, table_name_tokenize=table_name_tokenize, table_name_embed=table_name_embed, model_name=None):


    listofhashes = tuple(df_Save.row_hash.unique())

    query = text(f"""
        SELECT row_hash, row_hash_model, embed FROM {table_name_embed}
        WHERE model_name = '{model_name}' AND
        row_hash IN :hashes
    """)

    with db.conn_read() as conn: 
        df_embed = pd.read_sql_query(query, conn, params={"hashes": listofhashes})
   
    return df_embed

def selectModel(model_name, db):

    df_Save = getRankingTable(db)
    
    embed_df = getRelevantEmbeds(df_Save, db, model_name=model_name)


    df_Save = df_Save[['row_hash', 'Selection_Rank_Deterministic', 'Selection_Distance']].merge(embed_df[['row_hash', 'row_hash_model', 'embed']], how='left', on='row_hash')
    df_Save['disambigcycles'] = 0

    Master_df = getLabeledNodes(db=db, table_name_masterLabels=table_name_masterLabels)
    Master_df = Master_df.drop(columns='row_hash_model')
    Master_df = Master_df.merge(df_Save[['row_hash', 'row_hash_model', 'embed', 'Selection_Rank_Deterministic', 'disambigcycles']], how='left', on='row_hash')

    return Master_df, df_Save


def reverseL1(x, thresh=1):
    return (len(x) - sum(pd.notna(i) for i in x)) <= thresh
def standardizeNoneValues(x, removeNone=False):
    
    cleaned = [i for i in x if pd.notna(i)]
    if removeNone:
        return cleaned
    if len(cleaned) < len(x):
        cleaned.append(None)
    return frozenset(cleaned)


def ReverseprePropogate(db, RunCheck, model_name_list=None):  
    
    
    decon = PlumGen_ORCA(max_workers=4,
                initialstepsize=50, v_thresh_start=0.50,
                labels_col='user_label_standard',
                includeClosestinPool=True,
                keeploopinguntilProgress=False,
                clusterGapFactor = 'min_same + (max_diff - min_same)/2',
                RunCheck=RunCheck)

    if model_name_list is None:
        query = f'SELECT DISTINCT(model_name) FROM {table_name_embed}'
        models = []
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):models.append(df)
            
        models = pd.concat(models)
        models = models.reset_index(drop=True)
        model_name_list = set(models.model_name)
        model_name_list = list(model_name_list)



    for model_name in model_name_list:
        print(model_name)
        Master_df, df_Save=selectModel(model_name, db)

        TierOne_df_working = df_Save.drop(Master_df.index)

        df_Save['user_label_standard'] = df_Save.row_hash_model.map(Master_df.set_index('row_hash_model')['user_label_standard'].to_dict())
        df_Save['confidence'] = df_Save.row_hash_model.map(Master_df.set_index('row_hash_model')['confidence'].to_dict()).fillna(0)

        df = df_Save.copy()

        Graph_df = decon.runL1Batch(df.copy(), df_Save.copy(), returnEntireSet=True)



        temp = Graph_df[Graph_df.row_hash.isin(Master_df.row_hash)].copy()
        temp = temp[temp['Category_Reassign_L1'].apply(reverseL1)]
        temp['Category_Reassign_L1'] = temp['Category_Reassign_L1'].apply(standardizeNoneValues)
        temp = temp[temp.Category_Reassign_L1.apply(len)==2]


        unlabeled_rowHashModel = set(TierOne_df_working.row_hash_model)

        recollectAll=[]
        for rows in temp.iterrows():
            for items in rows[1].Category_Reassign_L1_Source:
                if items in unlabeled_rowHashModel:
                    recollectAll.append((items,[i for i in list(rows[1].Category_Reassign_L1) if not pd.isna(i)][0], rows[1].confidence))
        recollectAll_df = pd.DataFrame(recollectAll).drop_duplicates()
        recollectAll_df.columns = ['row_hash_model', 'L1_reconcile', 'confidence']  
        # Grouped summaries
        recon = recollectAll_df.groupby('row_hash_model')['L1_reconcile'].unique().reset_index()
        conf  = recollectAll_df.groupby('row_hash_model')['confidence'].mean().reset_index()

        # Merge on row_hash_model
        merged = pd.merge(recon, conf, on='row_hash_model')

        recollectAll_df = merged[merged.L1_reconcile.apply(len)==1]
        recollectAll_df['L1_reconcile'] = recollectAll_df.L1_reconcile.apply(lambda x:x[0])
        TierOne_df_working = TierOne_df_working.merge(recollectAll_df, how='left', on='row_hash_model')

        temp_df = TierOne_df_working[~TierOne_df_working.L1_reconcile.isna()]
        temp_df = temp_df.rename(columns={'L1_reconcile':'user_label_standard'})

        temp_df['timestamp'] = time.time()
        temp_df = temp_df.drop(columns = ['Selection_Rank_Deterministic', 'Selection_Distance', 'embed', 'disambigcycles'])

        temp_df['computehardware'] = computeHardware 
        
        temp_df.columns = [col.lower() for col in temp_df.columns]

        rows_to_insert = temp_df.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name_reverseprepropogationtable,
            rows=rows_to_insert,
            conflict_key="row_hash_model",
            do_update=True,
            batch_size=500
        )

        print(f"Injected Model: {model_name}")
    
    return True