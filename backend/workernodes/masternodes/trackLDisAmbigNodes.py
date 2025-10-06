import os
import pandas as pd
import numpy as np
import joblib
from scipy.special import expit
from pathlib import Path

import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names.*", category=UserWarning)

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))    
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_ReverseprePropogation = os.environ.get("REVERSEPREPROPOGATEDLABELS")
table_name_disambiguationtable = os.environ.get("DISAMBIGUATIONLABELS") 




MODEL_PATH = Path(__file__).resolve().parent / "logistic_model.joblib"
model_reload = joblib.load(MODEL_PATH)

def PredictLogisticFromModel(row, model=model_reload):
    # Ensure row is reshaped for scikit-learn
    logit = model.decision_function([row])[0]
    return expit(logit)

def trackLDisAmbigNodes(db):

    query = f"""
    SELECT id, *
    FROM {table_name_disambiguationtable}
    """

    list_rank_df = []
    for df in db.resilient_read_query_keyset(query, chunksize=500):
        list_rank_df.append(df)
    if len(list_rank_df)<1:
        return False
    Disambiguated_df = pd.concat(list_rank_df)
    
    temp1 = pd.DataFrame(Disambiguated_df.groupby(by=['row_hash', 'user_label_standard']).size())
    temp1 = temp1.reset_index() 

    temp1.columns = ['row_hash', 'user_label_standard', 'model_votes']
    Disambiguated_df = Disambiguated_df.merge(temp1, how='left', on=['row_hash', 'user_label_standard'])
    Disambiguated_df = Disambiguated_df.drop(columns='id')

    temp = Disambiguated_df.copy()#[Disambiguated_df.user_label_standard_source_count>0]

    temp['user_label_standard_source_count'] = temp.user_label_standard_source.apply(len)
    temp['numberofrounds'] = pd.to_numeric(temp.numberofrounds, errors='coerce')
    temp['numberofrounds'] = temp.numberofrounds.fillna(0)

    temp = temp.sort_values(by=['model_votes', 'user_label_standard_source_count', 'numberofrounds']).drop_duplicates(subset=['row_hash'], keep='last')
    
    numeric_cols = temp.select_dtypes(include='number').columns

    for col in numeric_cols:
        col_min = temp[col].min()
        col_max = temp[col].max()
        if col_max == col_min:
            temp[col] = 0 # or any constant value
        else:
            temp[col] = (temp[col] - col_min) / (col_max - col_min)
        
        
    # Load the model
    Disambiguated_df = Disambiguated_df[Disambiguated_df.index.isin(temp.index)]

    Disambiguated_df['confidence_aggregate'] = temp[['numberofrounds', 'confidence', 'user_label_standard_source_count', 'model_votes']].apply(lambda row: PredictLogisticFromModel(row), axis=1)

    Disambiguated_df['confidence'] = Disambiguated_df.confidence_aggregate 
    Disambiguated_df['method'] = 'DisAmbiguation'
    Disambiguated_df.loc[Disambiguated_df[Disambiguated_df.user_label_standard_source.apply(len)==0].index, 'method'] = 'L1_Propogation'
            
    Disambiguated_df = Disambiguated_df.drop(columns=['confidence_aggregate', 'category_reassign_l1_source', 'user_label_standard_source'])
    Disambiguated_df = Disambiguated_df.rename(columns={'user_label_standard':'label'}) 

        

    
    

        
    Disambiguated_df = Disambiguated_df.drop(columns=['numberofrounds'])
     
    rows_to_insert = Disambiguated_df.to_dict(orient='records')
    db.insert_into_table(
        table_name=table_name_masterLabels,
        rows=rows_to_insert,
        batch_size=500,
        conflict_key="row_hash",        
        where_flag=True
    )   
        
    return True                