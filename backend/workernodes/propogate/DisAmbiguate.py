import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import pandas as pd

warnings.filterwarnings("ignore", message="A value is trying to be set on a copy")
#import torch
computeHardware = 'CPU'
#if torch.cuda.is_available():
#    computeHardware = 'GPU'
    

import sys
from tqdm import tqdm
import os
import time 
import numpy as np
from .PlumGen_ORCA import PlumGen_ORCA
from .selectModel import selectModel
from .RetrieveDuplicateCheckFlag import RetrieveDuplicateCheckFlag

import faiss

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))
table_name_disambiguationtable = os.environ.get("DISAMBIGUATIONLABELS")
DISAMBIGUATIONDISSECTIONTHRESHOLD = float(os.environ.get("DISAMBIGUATIONDISSECTIONTHRESHOLD", "0.001"))



def DisAmbiguate(db, RunCheck, model_name_list=None, taskManager=None, stringtoPass=None):
        
    duplicateListIDs = RetrieveDuplicateCheckFlag(db)
    

    
    requireLockRefresh = False
    if model_name_list is None:
        query = f'SELECT DISTINCT(model_name) FROM {table_name_embed}'
        models = []
        # with engine.connect() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):models.append(df)
            
        models = pd.concat(models)
        models = models.reset_index(drop=True)
        model_name_list = set(models.model_name)
        model_name_list = list(model_name_list)
    else:
        requireLockRefresh = True
        abletoRenewLock = True
        
    for model_name in model_name_list:
        
        decon = PlumGen_ORCA( 
                    initialstepsize=50, v_thresh_start=0.50, 
                    labels_col='user_label_standard',
                    includeClosestinPool=False,
                    keeploopinguntilProgress=False,
                    clusterGapFactor = 'min_same + (max_diff - min_same)/2',
                    RunCheck=RunCheck,
                    flag_only_l1_combinations=True,
                    duplicateListIDs=duplicateListIDs,
                    reftotargetRatio=8,
                    ExcludeL1Duplicates=True) 
                
        print(model_name)
        Master_df, Ambiguous_df=selectModel(model_name, db, disAmbig=True)
        if Master_df.shape[0] == Ambiguous_df.shape[0]:continue
                
        print(Master_df.shape)
        print(Ambiguous_df.shape)
        
        Ambiguous_df_thisround_list = decon.ChunkbyL1CombinationsEven(Ambiguous_df, Master_df)
        Masterdf=Master_df
        emb_base = np.vstack(Master_df.embed).astype('float32')
        faiss.normalize_L2(emb_base)
        min_same, max_diff          = decon.compute_dynamic_threshold(Master_df, emb_base)
        
#        Masterdf, Ambiguous_df_thisround_list, min_same, max_diff, df = decon.prePropogate(Save_df, Master_df, additional_Ranks=[])

        print(f"Sample Distribution: {Masterdf.groupby(by=decon.labels_col).size()}")
        print(f"Sampled: {Masterdf.shape[0]} rows | Gap Ratio: {round((1 - max_diff) / (1 - min_same) * 100, 1)}%")
        print(f"min_same: {min_same:.4f}, max_diff: {max_diff:.4f}")
        print(f'Threshold: {DISAMBIGUATIONDISSECTIONTHRESHOLD}')
        print(f"actual threshold: {round((1 - max_diff) / (1 - min_same) * 100, 1)}")
        print("Type check:", type(min_same), type(max_diff), type(DISAMBIGUATIONDISSECTIONTHRESHOLD))

        threshold_val = float(DISAMBIGUATIONDISSECTIONTHRESHOLD)
        if round((1 - max_diff) / (1 - min_same) * 100, 1) < threshold_val:
            continue
        #if round((1 - max_diff) / (1 - min_same) * 100, 1)<DISAMBIGUATIONDISSECTIONTHRESHOLD:continue #maybe too close to be able to accurately dissect
        #min_same is the minimum similarity between same class, so this is the farthest two points in the same class
        #max_diff is the maximum similarity between different class, so this is the closest two points in different class, meaning the borderline case
        
        for roundcount, TierOne_df in enumerate(tqdm(Ambiguous_df_thisround_list)):
            if requireLockRefresh: #refresh lock
                abletoRenewLock = taskManager.renew_lock(db, stringtoPass)
                if not abletoRenewLock: break
                
            TierOne_df_working = TierOne_df.copy()
            disambigcycles_dict = {key:values+1 for key, values in Ambiguous_df[Ambiguous_df.row_hash_model.isin(TierOne_df_working.row_hash_model)].set_index('row_hash_model')['disambigcycles'].to_dict().items()}
            Ambiguous_df['disambigcycles'] = Ambiguous_df.row_hash_model.map(disambigcycles_dict).fillna(Ambiguous_df.disambigcycles)

            print(f"Get size of object PlumGen ORCA: {sys.getsizeof(decon)}")
            
            Masterdf, TierOne_df_working_returned, min_same, max_diff, v_measure = decon.Run(Masterdf, TierOne_df_working)
            print(round((1-max_diff)/(1-min_same)*100,1), min_same, max_diff, v_measure)
            print(f"Size of Labeled Nodes: {Masterdf.shape[0]}")

        if requireLockRefresh: #refresh lock
            if not abletoRenewLock: continue
                
        Masterdf = Masterdf[~Masterdf.row_hash_model.isin(Master_df.row_hash_model)]
        print(f"Nodes Labeled this Round: {Masterdf.shape[0]}")
                    
        if Masterdf.shape[0]<1: continue

        Masterdf['user_label_standard_confidence'] = Masterdf.user_label_standard_confidence.fillna(Masterdf.confidence)
        Masterdf['confidence'] = Masterdf.user_label_standard_confidence

        Masterdf = decon.runDuplicateSanityCheck(Masterdf)
        
        Masterdf = Masterdf[['row_hash', 'confidence', 'timestamp', 'user_label_standard',
            'row_hash_model', 'user_label_standard_source', 'Category_Reassign_L1_Source', 'numberofrounds']]  

        Masterdf['timestamp'] = time.time()
        Masterdf['computehardware'] = computeHardware 
                

        Masterdf.columns = [col.lower() for col in Masterdf.columns]

        Masterdf['user_label_standard_source'] = Masterdf['user_label_standard_source'].apply(lambda x: x if isinstance(x, list) else [str(x)] if pd.notna(x) else [])
        Masterdf['category_reassign_l1_source'] = Masterdf['category_reassign_l1_source'].apply(lambda x: x if isinstance(x, list) else [str(x)] if pd.notna(x) else [])

        print("decon.listofpreviousNDims")
        print(decon.listofpreviousNDims)
        
        
        
        rows_to_insert = Masterdf.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name_disambiguationtable,
            rows=rows_to_insert,
            conflict_key="row_hash_model",
            do_update=True,
            batch_size=500
        )    

        del Masterdf, Ambiguous_df, Master_df
        
    return True                