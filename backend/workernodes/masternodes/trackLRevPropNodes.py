import os
import pandas as pd
import numpy as np

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))    
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_ReverseprePropogation = os.environ.get("REVERSEPREPROPOGATEDLABELS")
table_name_tokenize = os.environ.get("TOKENIZEDATATEXTTABLE")

def prePropogationConfidence(model_votes, confidence):
    return max(min(0.0591 * model_votes + 0.0565 * confidence + 0.6472, 1), 0)

def trackLRevPropNodes(db):

    query = f"""
    SELECT id, *
    FROM {table_name_ReverseprePropogation}
    """

    list_rank_df = []
    for df in db.resilient_read_query_keyset(query, chunksize=500):
        list_rank_df.append(df)
    if len(list_rank_df)<1:
        return False        
    ReverseprePropogated_df = pd.concat(list_rank_df)

    ReverseprePropogated_df = ReverseprePropogated_df.sort_values(by='confidence').drop_duplicates(subset=['row_hash', 'row_hash_model'], keep='last')

    temp = pd.DataFrame(ReverseprePropogated_df.groupby(by=['row_hash', 'user_label_standard']).size())
    temp = temp.reset_index()

    temp.columns = ['row_hash', 'user_label_standard', 'model_votes']
    ReverseprePropogated_df = ReverseprePropogated_df.merge(temp, how='left', on=['row_hash', 'user_label_standard'])
    ReverseprePropogated_df = ReverseprePropogated_df.drop(columns='id')

    ReverseprePropogated_df['confidence_aggregate'] = ReverseprePropogated_df.apply(lambda row: prePropogationConfidence(row['model_votes'], row['confidence']), axis=1)

    ReverseprePropogated_df['confidence'] = ReverseprePropogated_df.confidence_aggregate 
    ReverseprePropogated_df = ReverseprePropogated_df.drop(columns=['confidence_aggregate', 'category_reassign_l1_source'])
    ReverseprePropogated_df = ReverseprePropogated_df.rename(columns={'user_label_standard':'label'}) 
    ReverseprePropogated_df['method'] = 'Reverse_L1_Propogation'
      
    ReverseprePropogated_df = ReverseprePropogated_df.sort_values(by='confidence').drop_duplicates(subset='row_hash', keep='last')  
        
    rows_to_insert = ReverseprePropogated_df.to_dict(orient='records')
    db.insert_into_table(
        table_name=table_name_masterLabels,
        rows=rows_to_insert,
        batch_size=500,
        conflict_key=["row_hash", "row_hash_model"],     
        where_flag=True
    )   
        
    return True                