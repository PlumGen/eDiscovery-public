import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="A value is trying to be set on a copy")
import pandas as pd
import numpy as np

import os
from .PlumGen_ORCA import PlumGen_ORCA
from .selectModel import selectModel
from .RetrieveDuplicateCheckFlag import RetrieveDuplicateCheckFlag 

import torch
computeHardware = 'CPU'
if torch.cuda.is_available():
    computeHardware = 'GPU'



if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    

table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_prepropogationtable = os.environ.get("PREPROPOGATEDLABELS")
ambiguousset_tablename = os.environ.get("AMBIGUOUSSETTABLE")

# Force all numpy numeric scalars into Python native floats/ints
def ensure_python_type(x):
    if isinstance(x, np.generic):       # numpy scalar
        return x.item()
    elif isinstance(x, list):           # lists of numpy scalars
        return [ensure_python_type(i) for i in x]
    else:
        return x
    
def runPrePropogation(db, RunCheck, model_name_list=None):  
    
    duplicateListIDs = RetrieveDuplicateCheckFlag(db)
    decon = PlumGen_ORCA(max_workers=4,
                initialstepsize=50, v_thresh_start=0.50,
                labels_col='user_label_standard',
                includeClosestinPool=True,
                keeploopinguntilProgress=False,
                flag_only_l1_combinations=True,
                clusterGapFactor = 'min_same + (max_diff - min_same)/2',
                RunCheck=RunCheck,
                duplicateListIDs=duplicateListIDs)
    
 
    if model_name_list is None:
        query = f'SELECT DISTINCT(model_name) FROM {table_name_embed}'
        # with engine.connect() as conn:
        with db.conn_read() as conn:
            models = pd.read_sql_query(query, conn)
            model_name_list = models.model_name.to_list()


    for model_name in model_name_list:
        print(model_name)
        Master_df, df_Save=selectModel(model_name, db)

        if Master_df.shape[0] == df_Save.shape[0]:continue
        
        print(Master_df.shape)
        print(df_Save.shape)
        
        # while True:
        #     Master_df, df_Save = decon.startORCAPropogation(df_Save, Master_df)
        Masterdf, Ambiguous_df_thisround_list, min_same, max_diff, df = decon.prePropogate(df_Save, Master_df, additional_Ranks=[])       

        if Masterdf.shape[0] == Master_df.shape[0]:continue
        
        Masterdf = Masterdf[~Masterdf.Category_Reassign_L1_Source.isna()]
        
        Masterdf = decon.runDuplicateSanityCheck(Masterdf)
            
        Masterdf = Masterdf.drop(columns=['id', 'user_label_actual', 'model_votes', 'label_distribution', 'embed', 'Selection_Rank_Deterministic',
            'disambigcycles', 'Selection_Distance', 'Category_Reassign_L1', 'Category_Reassign_L1_distance',
            'Category_Reassign_L1_confidence', 'method', 'user_reassign'])
        
        Masterdf['computehardware'] = computeHardware 
                
        Masterdf.columns = [col.lower() for col in Masterdf.columns]
        
        rows_to_insert = Masterdf.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name_prepropogationtable,
            rows=rows_to_insert,
            conflict_key="row_hash_model",
            do_update=True,
            batch_size=500
        )
        
        Ambiguous_df_thisround = pd.concat(Ambiguous_df_thisround_list)

        Ambiguous_df_thisround.columns = [col.lower() for col in Ambiguous_df_thisround.columns]
        Ambiguous_df_thisround = Ambiguous_df_thisround[['row_hash', 'row_hash_model', 'category_reassign_l1_source',
            'confidence', 'timestamp', 'lowest_difference',
            'user_label_standard_frozen', 'user_label_standard', 'category_reassign_l1', 'category_reassign_l1_distance',
            'category_reassign_l1_confidence']]
        Ambiguous_df_thisround['user_label_standard_frozen'] = Ambiguous_df_thisround.user_label_standard_frozen.apply(list)
        Ambiguous_df_thisround.columns = [col.lower() for col in Ambiguous_df_thisround.columns]

        Ambiguous_df_thisround = Ambiguous_df_thisround.applymap(ensure_python_type)
        Ambiguous_df_thisround = Ambiguous_df_thisround.where(Ambiguous_df_thisround.notnull(), None)
                
        rows_to_insert_second = Ambiguous_df_thisround.to_dict(orient='records')
        db.insert_into_table(
            table_name=ambiguousset_tablename,
            rows=rows_to_insert_second,
            conflict_key="row_hash_model",
            do_update=True,
            batch_size=500
        )
            
    return True