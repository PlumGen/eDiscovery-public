
import os
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))    
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_prePropogation = os.environ.get("PREPROPOGATEDLABELS")
table_name_tokenize = os.environ.get("TOKENIZEDATATEXTTABLE")

MODEL_PATH = Path(__file__).resolve().parent / "L1Propogation_AggregateConfidence.joblib"
model_reload = joblib.load(MODEL_PATH)

def PredictConfidenceFromModel(row, model=model_reload):
    return np.clip(model.predict([row])[0], 0, 1)

def trackLPropNodes(db):

    query = f"""
    SELECT id, *
    FROM {table_name_prePropogation}
    """

    list_rank_df = []
    for df in db.resilient_read_query_keyset(query, chunksize=500):
        list_rank_df.append(df)
    if len(list_rank_df)<1:return False
    prePropogated_df = pd.concat(list_rank_df)

    prePropogated_df = prePropogated_df.sort_values(by='confidence').drop_duplicates(subset=['row_hash', 'row_hash_model'], keep='last')

    temp = pd.DataFrame(prePropogated_df.groupby(by=['row_hash', 'user_label_standard']).size())
    temp = temp.reset_index() 

    temp.columns = ['row_hash', 'user_label_standard', 'model_votes']
    prePropogated_df = prePropogated_df.merge(temp, how='left', on=['row_hash', 'user_label_standard'])
    prePropogated_df = prePropogated_df.drop(columns='id')

    # prePropogated_df['confidence_aggregate'] = prePropogated_df.apply(lambda row: DisambigConfidence(row['model_votes'], row['confidence']), axis=1)
    # prePropogated_df['confidence'] = prePropogated_df.confidence_aggregate 

        
    prePropogated_df = prePropogated_df.sort_values(by=['model_votes', 'confidence']).drop_duplicates(subset='row_hash', keep='last')   

    #prePropogated_df['user_label_standard_source_count'] = prePropogated_df.user_label_standard_source.apply(lambda x: len(x) if isinstance(x, list) else 0)
    prePropogated_df['category_reassign_l1_source_count'] = prePropogated_df.category_reassign_l1_source.apply(lambda x: len(x) if isinstance(x, list) else 0)

    prePropogated_df['confidence_aggregate'] = prePropogated_df[['model_votes', 'confidence', 'category_reassign_l1_source_count']].apply(lambda row: PredictConfidenceFromModel(row), axis=1)

    prePropogated_df['confidence'] = prePropogated_df.confidence_aggregate 

    prePropogated_df = prePropogated_df.rename(columns={'user_label_standard':'label'}) 
    prePropogated_df['method'] = 'L1_Propogation'

    prePropogated_df = prePropogated_df.sort_values(by='confidence').drop_duplicates(subset='row_hash', keep='last') 
    prePropogated_df = prePropogated_df.drop(columns=['category_reassign_l1_source','category_reassign_l1_source_count', 'confidence_aggregate'])

    rows_to_insert = prePropogated_df.to_dict(orient='records')
    db.insert_into_table(
        table_name=table_name_masterLabels,
        rows=rows_to_insert,
        batch_size=500,
        conflict_key="row_hash",        
        where_flag=True
    )   
        
    return True                