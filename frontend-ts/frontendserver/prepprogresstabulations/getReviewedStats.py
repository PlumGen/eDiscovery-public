from sqlalchemy import Table, Column, text, String, select, inspect
import os
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text


import pandas as pd
import numpy as np
import os


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
    


def getReviewedStats(selected_db):

    # 1 number of documents ingested as raw text
    query_entire = f"""
        SELECT COUNT(DISTINCT docid)
        FROM rawdatatext    
    """
    with selected_db.conn_read() as conn:
        result = conn.execute(text(query_entire)).scalar()

    numberofdocumentsIngested = result


    query_entire = f"""
        SELECT *
        FROM {table_name_masterLabels}
    """

    with selected_db.conn_read() as conn:
        result = conn.execute(text(query_entire))
        columns = result.keys()  # get column names
        result_df = pd.DataFrame(result.fetchall(), columns=columns)

    result_df['Results'] = result_df.user_reassign==result_df.label


    query = text(f"""
        SELECT DISTINCT ON (user_label_code) *
        FROM {table_name_labelcandidates}
    """)

    with selected_db.conn_read() as conn:
        result = conn.execute(query)
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]

    labelmapping = {i['user_label_code']:list(frozenset(i['user_label'])) for i in thisTexts} 

    reviewedPerIssue = result_df[~result_df.user_reassign.isna()].groupby('label').size().to_dict()
    acceptedPerIssue = result_df[~result_df.user_reassign.isna()].groupby('label')['Results'].sum().to_dict()
    acceptedPerIssue = dict(sorted(acceptedPerIssue.items()))


    recreateDict=dict()
    for idx, (key, values) in enumerate(acceptedPerIssue.items()):


        recreateDict.update({idx:{'issuecode':key,
                                 'displayname':'\n'.join([i[:50] for i in labelmapping[key]]),
                                 'completeName':labelmapping[key],
                                'totalreviewed':reviewedPerIssue[key],
                                'acceptedRatio':int(acceptedPerIssue[key]/reviewedPerIssue[key]*100),
                                }})
        
    return recreateDict