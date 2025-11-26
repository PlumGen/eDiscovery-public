### determine document level aggregation
import os
import pandas as pd
from collections import defaultdict
from scipy.stats import entropy

from sqlalchemy import inspect
from database_manager import DatabaseManager
import os
from sqlalchemy import Table, Column, text, String, select, inspect, func


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)

table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_cleantext = os.environ.get("CLEANEDDATATEXTTABLE")
chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))
aggregateConfidence = {'DisAmbiguation':0.70, 'L1_Propogation':0.96, 'user_manual':1}



def label_entropy(dist):
    total = sum(dist.values())
    probs = [v / total for v in dist.values()]
    return entropy(probs)

def normalizedistribution(dist):

    # Weighted score = count * mean_confidence
    weighted_scores = {k: v['count'] * v['mean_confidence'] for k, v in dist.items()}
    total = sum(weighted_scores.values())
    normalized_distribution = {k: round(v / total, 4) for k, v in weighted_scores.items()}
    
    return normalized_distribution

def flattenLabelDistribution(x):
    local_dict = {}
    for keys, values in x.items():
        values['mean_confidence'] = round(values['mean_confidence'],2)
        local_dict.update({keys[1]:values})
        
    return local_dict


def getdocumentlevelsummary(db):
    query = text(f"""
    SELECT docid, row_hash
    FROM {table_name_cleantext}
    """)

    with db.conn_read() as conn:
        documentID_df = pd.read_sql_query(query, conn)
    documentID_df = documentID_df.rename(columns={'docid':'document_unique_hash'})  


    subquery = f"""
    SELECT id
    FROM (
        SELECT id, row_hash, confidence,
            ROW_NUMBER() OVER (PARTITION BY row_hash ORDER BY confidence DESC, id) AS rank
        FROM {table_name_masterLabels}
    ) sub
    WHERE rank = 1
    """

    query = text(f"""
    SELECT *
    FROM {table_name_masterLabels}
    WHERE id IN ({subquery})
    """)

    list_rank_df = []
    for df in db.resilient_read_query_keyset(query, key_column='id', chunksize=chunksize):
        list_rank_df.append(df)
    Master_df = pd.concat(list_rank_df)


    
    Master_df = Master_df.merge(documentID_df, on='row_hash', how='left')
    # Master_df['aggregateConfidence'] = Master_df.method.map(aggregateConfidence)
    Master_df['aggregateConfidence'] = Master_df['confidence']#Master_df[['confidence', 'aggregateConfidence']].min(axis=1)

    label_conf_dist = (
        Master_df.groupby(['document_unique_hash', 'label'])
        .aggregate(mean_confidence=('aggregateConfidence', 'mean'), count=('label', 'size'))
        .groupby(level=0)
        .apply(lambda x: x[['count', 'mean_confidence']].to_dict(orient='index'))
        .to_dict()
    )

    Master_df['labeldistribution'] = Master_df.document_unique_hash.map(label_conf_dist)
    Master_df['flattenLabelDistribution'] = Master_df.labeldistribution.apply(flattenLabelDistribution)

    labelDistributions = Master_df.drop_duplicates(subset='document_unique_hash')[['document_unique_hash', 'flattenLabelDistribution']]
    labelDistributions['normalizeddistribution'] = labelDistributions.flattenLabelDistribution.apply(normalizedistribution)


    labelDistributions['label_entropy'] = labelDistributions.normalizeddistribution.apply(label_entropy)

    return labelDistributions