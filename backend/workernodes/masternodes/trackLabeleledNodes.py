from sqlalchemy import Column 
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, text, MetaData, Table, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError
from tqdm import tqdm
import pandas as pd
import numpy as np
import os



import pandas as pd
import numpy as np

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))    
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_labelcandidates = os.environ.get("LABELCANDIDATESTABLE")
table_name_tokenize = os.environ.get("TOKENIZEDATATEXTTABLE")

def trackLabeleledNodes(db):
    
    query = f"""SELECT id,*
    FROM {table_name_labelcandidates}
    """

    print('db name')
    db_name = db.engine.url.database
    print(db_name)
    print(table_name_labelcandidates)


    print('table_name_labelcandidates')
    print(table_name_labelcandidates)
    
    list_rank_df=[]
    # with engine.connect() as conn:
    for df in db.resilient_read_query_keyset(query, chunksize=chunksize):list_rank_df.append(df)
    print('list_rank_df')
    print(list_rank_df)
    labeledNodes_df = pd.concat(list_rank_df, ignore_index=True)

    labeledNodes_df['user_label_frozen'] = labeledNodes_df.user_label.apply(frozenset)
    user_label_frozen_list = list(set(labeledNodes_df['user_label_frozen']))
    user_label_frozen_list.sort()

    rebuild_label_code={}
    for idx, label in enumerate(user_label_frozen_list):
        rebuild_label_code.update({label:f'labelcode_500{idx}'})


    labeledNodes_df['user_label_code'] = labeledNodes_df.user_label_frozen.map(rebuild_label_code)

    labeledNodes_df = labeledNodes_df.drop(columns=['user_label_frozen', 'id'])

    rows_to_insert = labeledNodes_df.to_dict(orient='records')
    db.insert_into_table(
        table_name=table_name_labelcandidates,
        rows=rows_to_insert,
        conflict_key="row_hash",
        do_update=True,
        batch_size=500
    )

    if 'row_hash' not in labeledNodes_df.columns:
        query = f"""SELECT id, row_hash, row_hash_model
        FROM {table_name_tokenize}
        WHERE row_hash_model IN :row_hash
        """
        parameters = {'row_hash':tuple(labeledNodes_df.row_hash_model)}

        list_rank_df=[]
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize, params=parameters):list_rank_df.append(df)
        rowhash_df = pd.concat(list_rank_df)

        labeledNodes_df['row_hash'] = labeledNodes_df.row_hash_model.map(rowhash_df.set_index('row_hash_model')['row_hash'].to_dict())

    labeledNodes_df = labeledNodes_df.rename(columns={'user_label_code':'label'}) 
    labeledNodes_df['method'] = 'user_manual'
    labeledNodes_df['confidence'] = 1
    labeledNodes_df  = labeledNodes_df.drop(columns=['model_name', 'user_label'])
    labeledNodes_df['computehardware'] = 'NotRelevant'

    labeledNodes_df = labeledNodes_df.sort_values(by='confidence').drop_duplicates(subset='row_hash', keep='last')   


    rows_to_insert = labeledNodes_df.to_dict(orient='records')
    db.insert_into_table(
        table_name=table_name_masterLabels,
        rows=rows_to_insert,
        conflict_key="row_hash",         
        batch_size=500
    )   

    return True                