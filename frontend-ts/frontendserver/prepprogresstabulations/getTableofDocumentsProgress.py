from sqlalchemy import Table, Column, text, String, select, inspect
import os
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text


import pandas as pd
import numpy as np
import os
from scipy.stats import entropy

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
#import controlcontainers.controllingcontainer_switch as controllingcontainer_switch 
BUCKETNAME = os.environ.get("BUCKETNAME")
table_name = os.environ.get("RAWDATATEXTTABLE")
progress_table_name  = os.environ.get("DATATEXTTABLESTATUS")
table_name_cleantext = os.environ.get("CLEANEDDATATEXTTABLE")
table_name_tokenize  = os.environ.get("TOKENIZEDATATEXTTABLE")
table_name_embed     = os.environ.get("EMBEDDATATEXTTABLE")
runembedoncpu        = os.environ.get("EMBEDONCPU")

table_name_simpairs         = os.environ.get("SIMPAIRSDATATEXTTABLE")
table_name_deduplicates     = os.environ.get("MARKEDDUPLICATESTEXTTABLE")
table_name_ranking          = os.environ.get("RANKINGDATATEXTTABLE")
table_name_clustering       = os.environ.get("CLUSTERINGDATATEXTTABLE")
table_name_labelcandidates       = os.environ.get("LABELCANDIDATESTABLE")
table_name_labelcandidates_validation = os.environ.get("LABELCANDIDATESVALIDATIONTABLE")
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_prepropogationtable = os.environ.get("PREPROPOGATEDLABELS")

issuedefinition_tablename = os.environ.get("LABELISSUEDEFINITIONS")
table_name__master_node_label_candidates = os.environ.get("MASTERNODELABELS")
table_name_rawtext     = os.environ.get("RAWDATATEXTTABLE")

ENABLELABELCHECK = os.getenv('ENABLELABELCHECK')    
    

    
def cols_gt_zero(row):
    return row.index[row > 0].tolist()

def getAccuracyDocumentLevel(label_dist_local):

    label_dist = label_dist_local.copy()

    # rows with a user reassignment
    mask = ~label_dist['user_reassign'].isna()
    if not mask.any():
        return {'documentLevelAccuracy': None, 'FalseNegative': None, 'TotalDocumentsReviewed':0}

    label_dist = label_dist[~label_dist['user_reassign'].isna()]
    
    label_dist['Results'] = label_dist['most_frequent']==label_dist['user_reassign']

    documentLevelAccuracy = int(round(label_dist[~label_dist['user_reassign'].isna()].Results.sum()/label_dist[~label_dist['user_reassign'].isna()].shape[0]*100,2))

    excludecolumns = ['docid', 'most_frequent', 'user_reassign', 'Total Nodes', 'label_entropy','Results']
    temp = label_dist[list(set(label_dist.columns)-set(excludecolumns))]


    label_dist["cols_gt_zero"] = temp.apply(cols_gt_zero, axis=1)
    label_dist['False Negative'] = label_dist.apply(lambda row: row['user_reassign'] not in row["cols_gt_zero"], axis=1)

    temp = label_dist[~label_dist['user_reassign'].isna()]
    FalseNegative = int(temp['False Negative'].sum()/temp.shape[0]*100)
    
    return {'documentLevelAccuracy':documentLevelAccuracy, 'FalseNegative':FalseNegative, 'TotalDocumentsReviewed':label_dist.shape[0]}




def getTableofDocumentsProgress(selected_db):


    query_entire = f"""
        SELECT r.docid AS docid, m.row_hash as row_hash, m.label as label, m.user_reassign as user_reassign, m.confidence as confidence
        FROM {table_name_masterLabels} m 
        JOIN {table_name_cleantext} c ON m.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """

    with selected_db.conn_read() as conn:
        result = conn.execute(text(query_entire))
        columns = result.keys()
        relevantrows = [dict(zip(columns, row)) for row in result.fetchall()]
    allLabeled_df = pd.DataFrame(relevantrows)
    allLabeled_df = allLabeled_df.drop_duplicates(subset=['docid', 'row_hash'])

    label_dist = allLabeled_df.groupby('docid')['label'].value_counts().unstack(fill_value=0)

    # Sum confidence values grouped by docid and label
    conf_adjusted = allLabeled_df.groupby(['docid', 'label'])['confidence'].sum().unstack(fill_value=0)

    # Normalize to get confidence-weighted label probabilities per docid
    conf_probs = conf_adjusted.div(conf_adjusted.sum(axis=1), axis=0)

    label_confidence_dist = conf_probs*label_dist

    labelColumns = list(label_confidence_dist.columns)
    label_confidence_dist = label_confidence_dist[labelColumns].div(label_confidence_dist[labelColumns].sum(axis=1), axis=0)  # normalize to probabilities
    label_confidence_dist['most_frequent'] = label_confidence_dist[labelColumns].idxmax(axis=1)

    label_confidence_dist['label_entropy'] = label_confidence_dist[labelColumns].apply(entropy, axis=1)  # compute entropy per docid
    label_confidence_dist['user_reassign'] = label_confidence_dist.index.map(allLabeled_df[~allLabeled_df.user_reassign.isna()].set_index('docid')['user_reassign'].to_dict())
    label_dist_validation = label_confidence_dist[~label_confidence_dist.user_reassign.isna()]

    label_dist = label_dist.merge(label_confidence_dist[['most_frequent', 'label_entropy', 'user_reassign']], how='left', right_index=True, left_index=True)


    query_entire = f"""
        SELECT r.docid AS docid, c.row_hash as row_hash
        FROM {table_name_cleantext} c
        JOIN rawdatatext r ON c.docid = r.row_hash
    """

    with selected_db.conn_read() as conn:
        result = conn.execute(text(query_entire))
        columns = result.keys()
        alldocuments = [dict(zip(columns, row)) for row in result.fetchall()]


    label_dist['Total Nodes'] = label_dist.index.map(pd.DataFrame(alldocuments).groupby('docid').size().to_dict())


    reconstructColumns = ['most_frequent', 'user_reassign', 'Total Nodes', 'label_entropy']
    listofcolumns = label_dist.columns
    listofcolumns = [i for i in listofcolumns if i not in reconstructColumns]
    listofcolumns.sort()
    reconstructColumns.extend(listofcolumns)
    label_dist = label_dist[reconstructColumns]

    query = text(f"""
        SELECT DISTINCT ON (user_label_code) *
        FROM {table_name_labelcandidates}
    """)

    with selected_db.conn_read() as conn:
        result = conn.execute(query)
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]

    labelmapping = {i['user_label_code']:list(frozenset(i['user_label'])) for i in thisTexts}
    

    
    labelmapping = {i:' '.join(labelmapping[i])[:3] for i in listofcolumns}
    label_dist = label_dist.rename(columns=labelmapping)
    label_dist['most_frequent'] = label_dist['most_frequent'].map(labelmapping)
    label_dist['user_reassign'] = label_dist['user_reassign'].map(labelmapping)
 
    accuracyDocuments = getAccuracyDocumentLevel(label_dist)
    
    label_dist = label_dist.rename(columns={'most_frequent':'Propogated Label', 'user_reassign':'User Label', 'label_entropy':'Entropy'})
    label_dist['Entropy'] = label_dist['Entropy'].apply(lambda x:round(x,2))
    label_dist = label_dist.reset_index()
    
    return {'accuracyDocuments':accuracyDocuments,
            'columns':list(label_dist.columns), 
            'rows':label_dist.replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict('records')}