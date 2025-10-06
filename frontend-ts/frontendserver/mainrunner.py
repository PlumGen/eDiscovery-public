from sqlalchemy import Table, Column, text, String, select, inspect
import os
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text
# # Import libraries
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading

import pandas as pd
import numpy as np
import os
import json 
import datetime
import csv    

import requests
from sqlalchemy import bindparam
from collections import Counter

from scipy.stats import entropy
from database_manager import DatabaseManager 

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
import controlcontainers.controllingcontainer_switch as controllingcontainer_switch 
import initializebuckets
initializebuckets.initializebuckets() 

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.storage.blob import BlobClient
credential = DefaultAzureCredential()
account_url = os.environ.get("AZURE_BLOB_ACCOUNT_URL")
blob_service = BlobServiceClient(account_url=account_url, credential=credential)
    
def initializeSimRangesDefinition(db, tolerance=0.005, percent_quantile=0.99):
        
    table_name_similaritypairs = os.environ["SIMPAIRSDATATEXTTABLE"]
    table_name_cleantext = os.environ["CLEANEDDATATEXTTABLE"]

    engine = db.get_engine() 
    
    
    with engine.connect() as conn:
        query = f"""
            WITH cutoff AS (
              SELECT percentile_cont({percent_quantile}) WITHIN GROUP (ORDER BY similarity) AS threshold
              FROM {table_name_similaritypairs}
            )
            SELECT similarity
            FROM {table_name_similaritypairs}
            WHERE similarity >= (SELECT threshold FROM cutoff)
        """
        df = pd.read_sql_query(query, conn)
        df = df.sort_values("similarity").reset_index(drop=True)
    
    lo = df.similarity.min()
    hi = df.similarity.max()
    
    return lo, hi
    
def get_single_nearest_sample(mid, engine):
    table_name = os.environ["SIMPAIRSDATATEXTTABLE"]

    query = text(f"""
        SELECT *
        FROM {table_name}
        WHERE source_num_sentence > 0 AND target_num_sentence > 0
        ORDER BY ABS(similarity - :mid)
        LIMIT 1
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"mid": float(mid)}).mappings().first()

    if result is None:
        return {"status": "error", "message": "No valid samples"}

    return {"status": "ok", "sample": result}


def get_candidate_sample(lo, hi, last_answer, projectselected, tolerance=0.005, percent_quantile=0.99):

    db = selectDB(projectselected=projectselected)
    engine = db.get_engine() 

    print('last_answer',last_answer)
    if last_answer!='y' and last_answer!='n':
        print('initializing similarity ranges')
        lo, hi = initializeSimRangesDefinition(db, tolerance=0.005, percent_quantile=0.99)


    else:
        if last_answer == "y":
            hi = (lo + hi) / 2
        else:
            lo = (lo + hi) / 2
    
        if hi - lo <= tolerance:
            final_cutoff = (lo + hi) / 2
            update_cutoff_in_db(final_cutoff, engine, db.metadata)
            ## run control switch here
            runControlSwitch_async(projectselected)
            return {"status": "complete", "final_cutoff": final_cutoff}

    mid = (lo + hi) / 2
    

    
    # Load environment vars
    sample = get_single_nearest_sample(mid, engine)


    # Get text
    source_hash = sample["sample"].source_row_hash
    target_hash = sample["sample"].target_row_hash
    similarity = sample["sample"].similarity

    with engine.connect() as conn:
        fetch_query = """
        SELECT clean_text
        FROM cleandatatext
        WHERE row_hash = :hash
        """
        source_text = conn.execute(text(fetch_query), {"hash": source_hash}).scalar() or "[Not found]"
        target_text = conn.execute(text(fetch_query), {"hash": target_hash}).scalar() or "[Not found]"

    return {
        "status": "in_progress",
        "lo": lo,
        "hi": hi,
        "similarity": similarity,
        "source_text": source_text,
        "target_text": target_text
    }

def update_cutoff_in_db(cutoff, engine, metadata):
    progress_table_name = os.environ["DATATEXTTABLESTATUS"]
    progress_table = Table(progress_table_name, metadata, autoload_with=engine)
    value_to_insert = f"DUPLICATEDEFINITION:{cutoff}"

    stmt = insert(progress_table).values(status_text=value_to_insert)
    stmt = stmt.on_conflict_do_update(
        index_elements=["status_text"],
        set_={"status_text": value_to_insert}
    )

    with engine.begin() as conn:
        conn.execute(stmt)

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

with open("selectionmap.json", "r") as f:
    selectionmap=json.load(f)
     


def getdocumentsLabeledProgress(projectselected=None):
    
    selected_db = selectDB(projectselected=projectselected) 
# 1 number of documents ingested as raw text
    query_entire = f"""
        SELECT COUNT(DISTINCT docid)
        FROM rawdatatext    
    """
    with selected_db.engine.connect() as conn:
        result = conn.execute(text(query_entire)).scalar()

    numberofdocumentsIngested = result



    query_entire = f"""
        SELECT 
            r.docid AS docid,  
            c.row_hash AS row_hash
        FROM {table_name_masterLabels} m 
        JOIN {table_name_embed} e ON m.row_hash = e.row_hash    
        JOIN {table_name_cleantext} c ON e.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """
    with selected_db.engine.connect() as conn:
        result = conn.execute(text(query_entire)).fetchall()
    AnyLabeling_df = pd.DataFrame(result).drop_duplicates()
    AnyLabeling_df  = pd.DataFrame(AnyLabeling_df.groupby('docid').size())
    AnyLabeling_df.columns=['anylabeled']

    query_entire = f"""
        SELECT 
            r.docid AS docid,  
            e.row_hash AS row_hash
        FROM {table_name_embed} e    
        JOIN {table_name_cleantext} c ON e.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """
    with selected_db.engine.connect() as conn:
        result = conn.execute(text(query_entire)).fetchall()
    Prpared_df = pd.DataFrame(result).drop_duplicates()
    Prpared_df  = pd.DataFrame(Prpared_df.groupby('docid').size())
    Prpared_df.columns=['prepared']
    CombinedLabeledDocuments = Prpared_df.merge(AnyLabeling_df, how='left', right_index=True, left_index=True)

    x_axis   = ['Ingested', 'Accepted', 'Rejected', 'Fully Labeled', 'Partially Labeled', 'Not Labeled']
    Ingested = [numberofdocumentsIngested, 0, 0]
    Accepted = [0, len(CombinedLabeledDocuments.index), 0]
    Rejected = [0, numberofdocumentsIngested-len(CombinedLabeledDocuments.index), 0]
    FullLabeled  = [0, 0, CombinedLabeledDocuments[CombinedLabeledDocuments.prepared==CombinedLabeledDocuments.anylabeled].shape[0]]
    PartiallyLabeled  = [0, 0, CombinedLabeledDocuments[(CombinedLabeledDocuments.prepared!=CombinedLabeledDocuments.anylabeled)&(CombinedLabeledDocuments.anylabeled>0)].shape[0]]
    NotLabeled  = [0, 0, CombinedLabeledDocuments[(CombinedLabeledDocuments.anylabeled==0)|(CombinedLabeledDocuments.anylabeled.isna())].shape[0]]



    data = [x_axis, Ingested, Accepted, Rejected, FullLabeled, PartiallyLabeled, NotLabeled]


    return {'tabledata':data,
    'percents':{'anylabeled':int(CombinedLabeledDocuments.anylabeled.sum()),
    'totalprepared':int(CombinedLabeledDocuments.prepared.sum())}}

    
def chevronsprogress(recreateDict):
    progress_chevron_mapping = {
      1: ["Data Ingestion"],
      2: ["Text Cleaning", "Tokenization", "Vectorization", "Similarity Pairs"],
      3: ["Near-Duplicates Definition"],
      4: ["Duplicates Marked", "Ranking", "Cluster", "Identify Label Candidates"],
      5: ["User Labeled"],
      6: ["Label Propogation"]
    }

    flat_stage_dict = {list(v.keys())[0]: list(v.values())[0] for v in recreateDict.values()}
    rebuild_chevron_progress={}
    for idx, stages in progress_chevron_mapping.items():
        completedStages = []
        for item in reversed(stages):
            if flat_stage_dict[item].get('completed')=='Yes':
                completedStages.append(item)
        if len(set(stages)-set(completedStages))==0:
            rebuild_chevron_progress.update({idx:{'status':'complete', 'finalstage':completedStages[0]}})
        elif len(set(stages)-set(completedStages))>0 and completedStages:
            rebuild_chevron_progress.update({idx:{'status':'pending', 'finalstage':completedStages[0]}})
        else:
            rebuild_chevron_progress.update({idx:{'status':'pending', 'finalstage':stages[0]}})

    if rebuild_chevron_progress[1]['status']=='pending':
        rebuild_chevron_progress[1]['color'] = 'red'
    else: rebuild_chevron_progress[1]['color'] = 'green'

    if rebuild_chevron_progress[2]['status']=='pending':
        rebuild_chevron_progress[2]['color'] = 'yellow'
    else: rebuild_chevron_progress[2]['color'] = 'green'

    if rebuild_chevron_progress[3]['status']=='pending' and rebuild_chevron_progress[2]['status']=='pending':
        rebuild_chevron_progress[3]['color'] = 'yellow'
    elif rebuild_chevron_progress[3]['status']=='complete':
        rebuild_chevron_progress[3]['color'] = 'green'
    if rebuild_chevron_progress[3]['status']=='pending' and rebuild_chevron_progress[2]['status']=='complete':
        rebuild_chevron_progress[3]['color'] = 'red'

    if rebuild_chevron_progress[4]['status']=='pending':
        rebuild_chevron_progress[4]['color'] = 'yellow'
    else: rebuild_chevron_progress[4]['color'] = 'green'

    if rebuild_chevron_progress[5]['status']=='pending' and rebuild_chevron_progress[4]['status']=='pending':
        rebuild_chevron_progress[5]['color'] = 'yellow'
    elif rebuild_chevron_progress[5]['status']=='complete':
        rebuild_chevron_progress[5]['color'] = 'green'
    if rebuild_chevron_progress[5]['status']=='pending' and rebuild_chevron_progress[4]['status']=='complete':
        rebuild_chevron_progress[5]['color'] = 'red'

    if rebuild_chevron_progress[6]['status']=='pending':
        rebuild_chevron_progress[6]['color'] = 'yellow'
    else: rebuild_chevron_progress[6]['color'] = 'green'

    return rebuild_chevron_progress

def getcurrentprogress(projectselected=None):
    
    label_df = pd.DataFrame(['1'], columns=['status_text'])
    
    if projectselected is None:
        return False
    
    db = selectDB(projectselected=projectselected)
    engine = db.get_engine()  
    inspector = inspect(engine)
    if inspector.has_table(progress_table_name):        
        query = f"""SELECT *
        FROM {progress_table_name}
        """
        list_label_df=[]
        with engine.connect() as conn:
            for df in db.resilient_read_query_keyset(query, chunksize=500):list_label_df.append(df)
        label_df = pd.concat(list_label_df)
    
    
    flat_stage_mapping = {
        'DATAINGESTCOMPLETE': 'Data Ingestion',
        'TEXTCLEANCOMPLETE': 'Text Cleaning',
        'TOKENIZECOMPLETE:ALL': 'Tokenization',
        'EMBEDCOMPLETE:ALL': 'Vectorization',
        'SIMPAIRSCOMPLETE': 'Similarity Pairs',
        'DUPLICATEDEFINITION': 'Near-Duplicates Definition',
        'DUPLICATESMARKEDCOMPLETE': 'Duplicates Marked',
        'RANKINGCOMPLETE': 'Ranking',
        'CLUSTERCOMPLETE:ALL': 'Cluster',
        'LABELCANDIDATECOMPLETE': 'Identify Label Candidates',
        'USERLABELEDNODES': 'User Labeled',
        'DISAMBIGUATIONCOMPLETE': 'Label Propogation'
    }
    
    
    
    stages = {key:{'completed':'No', 'children':[]} for key, items in flat_stage_mapping.items()}
    
    for keys, _ in stages.items():
        definition=False
        if keys=='DUPLICATEDEFINITION':
            definition=any(['DUPLICATEDEFINITION' in i for i in label_df.status_text.to_list()])
        
        if keys in label_df.status_text.to_list() or definition:
            stages[keys]['completed'] = 'Yes'
            if 'ALL' in keys:
                completedstages = [i.split(':')[1] for i in label_df.status_text.to_list() if keys.split(':')[0] in i]
                completedstages = [i for i in completedstages if i!='ALL']
                stages[keys]['children'] = completedstages
    
    
    recreateDict = dict()
    for xx, (key, items) in enumerate(stages.items()):
        recreateDict[xx] = {flat_stage_mapping[key]:items}
    
    
    return {'tree':recreateDict, 'chevron':chevronsprogress(recreateDict)}
    

def selectDB(projectselected=None):
    if projectselected is None:
        return False
 
    db = DatabaseManager(db_name=selectionmap[projectselected]['db_name'])
    
    return db
    
def getitemsinstorage(projectselected=None):

    if projectselected is None:
        data = [
            {
                'name': None,
                'size': None,
                'updated': None,
                'content_type':None,
            }
        ]

        return data
        
    container = blob_service.get_container_client(selectionmap[projectselected]['bucket'])
    data = []
    for item in container.list_blobs():
        props = container.get_blob_client(item.name).get_blob_properties()
        data.append({
            "name": item.name,
            "size": props.size,
            "updated": props.last_modified,
            "content_type": props.content_settings.content_type,
        })

    return data


def addnewdefinitiontotable(addnewcategory):
    
    db = selectDB(projectselected=addnewcategory['company'])
    engine = db.get_engine()  

    if 'category' in addnewcategory:
        insert_query = f"""
        INSERT INTO {issuedefinition_tablename} (issuedefinition)
        VALUES (:issuedefinition)
        """
        
        try:
            with engine.connect() as conn:
                conn.execute(text(insert_query), {'issuedefinition': addnewcategory['category']})
                conn.commit()  # if you're using autocommit=False
        except:pass
        
    query = f"""
    SELECT * FROM {issuedefinition_tablename}
    """
    with engine.connect() as conn:
        definitiontable = conn.execute(text(query))
        definitiontable = definitiontable.fetchall()

    currentlistofdefinitions = [dict(row._mapping) for row in definitiontable]
    
    return currentlistofdefinitions

def build_label_candidate_query(table_name, current_id=None, direction=None, label_filter=None, specific_row_hash_model=None):
    bind_params = {}
    where_clauses = []
    order_clause = ""
    
    if specific_row_hash_model is not None:
        where_clauses.append(f"row_hash_model ='{specific_row_hash_model}'")
    else:
        if current_id is not None and direction in ("next", "prev"):
            if current_id==1 and direction=='prev':current_id=2
            op = ">" if direction == "next" else "<"
            ordering = "ASC" if direction == "next" else "DESC"
            where_clauses.append(f"id {op} :current_id")
            bind_params["current_id"] = int(current_id)
            order_clause = f"ORDER BY id {ordering}"

        if label_filter == 'labeled':
            where_clauses.append("user_label IS NOT NULL")
        elif label_filter == 'unlabeled':
            where_clauses.append("user_label IS NULL")

    where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    query = f"""
    SELECT * FROM {table_name}
    {where_clause}
    {order_clause}
    LIMIT 1
    """

    return query.strip(), bind_params


def getNextLabelCandidate(getlabelCandidate):
    query, params = build_label_candidate_query(
        table_name=table_name_labelcandidates,
        current_id=getlabelCandidate['current_id'],
        direction=getlabelCandidate['direction'],
        label_filter=getlabelCandidate['onlyUnlabeled'],
        specific_row_hash_model=getlabelCandidate['specific_row_hash_model']
    )

    db = selectDB(projectselected=getlabelCandidate['company'])
    engine = db.get_engine()

    with engine.connect() as conn:
        countlabelCandidates = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name_labelcandidates}")
        ).scalar()

    with engine.connect() as conn:
        unlabeledCandidates = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name_labelcandidates} WHERE user_label is NULL")
        ).scalar()

    
    with engine.connect() as conn:
        result = conn.execute(text(query), params).fetchall()

    if not result:
        return {
            "chunk_text": "",
            "clean_text": "",
            "row_hash": "",
            "docid": "",
            "documenttext": "",
            "user_label": [],
            "id": "",
            "row_hash_model": "",
            "countlabelCandidates": countlabelCandidates,
            "unlabeledCandidates":unlabeledCandidates
        }

    ThislabelingCandidate = dict(result[0]._mapping)
    row_hashes = tuple([ThislabelingCandidate['row_hash_model']])

    query_entire = text("""
        SELECT r.docid AS docid, r."Body" as body, t.row_hash_model as row_hash_model
        FROM labelcandidates l
        JOIN tokenizeddata t ON l.row_hash_model = t.row_hash_model
        JOIN cleandatatext c ON t.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
        WHERE l.row_hash_model IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))

    query_chunk = text("""
        SELECT c.chunk_text AS chunk_text, c.clean_text as clean_text, c.row_hash as row_hash
        FROM labelcandidates l
        JOIN tokenizeddata t ON l.row_hash_model = t.row_hash_model
        JOIN cleandatatext c ON t.row_hash = c.row_hash
        WHERE l.row_hash_model IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))

    with engine.connect() as conn:
        entireTexts = conn.execute(query_entire, {'hashes': row_hashes}).fetchone()
        thisTexts = conn.execute(query_chunk, {'hashes': row_hashes}).fetchone()

    ThislabelingCandidate['chunk_text'] = thisTexts[0] if thisTexts else ""
    ThislabelingCandidate['clean_text'] = thisTexts[1] if thisTexts else ""
    ThislabelingCandidate['row_hash'] = thisTexts[2] if thisTexts else ""
    ThislabelingCandidate['docid'] = entireTexts[0] if entireTexts else ""
    ThislabelingCandidate['documenttext'] = entireTexts[1] if entireTexts else ""
    ThislabelingCandidate['countlabelCandidates'] = countlabelCandidates
    ThislabelingCandidate['unlabeledCandidates'] = unlabeledCandidates
           
    return ThislabelingCandidate



def get_topicdefinitions(getlabelCandidate):
    db = selectDB(projectselected=getlabelCandidate['company'])
    engine = db.get_engine()  

    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT label, COUNT(*) as count
            FROM {table_name__master_node_label_candidates}
            GROUP BY label
            ORDER BY count DESC
        """))
        label_counts = result.fetchall()

    label_counts = [{'label_code':label, 'counter':counts} for (label, counts) in label_counts]
    topicdefinitions = sorted(label_counts, key=lambda x: x["counter"], reverse=True)

    query = f"""
    SELECT * FROM {table_name_labelcandidates}
    """
    with engine.connect() as conn:
        definitiontable_labeled = conn.execute(text(query))
        definitiontable_labeled = definitiontable_labeled.fetchall()
    currentlistofdefinitions_labeled = [dict(row._mapping) for row in definitiontable_labeled]    

    currentlistofdefinitions_labeled = pd.DataFrame(currentlistofdefinitions_labeled)
    currentlistofdefinitions_labeled

    query = f"""
    SELECT * FROM {issuedefinition_tablename}
    """
    with engine.connect() as conn:
        definitiontable = conn.execute(text(query))
        definitiontable = definitiontable.fetchall()

    currentlistofdefinitions = [dict(row._mapping) for row in definitiontable]


    rebuildDefinitionCounts = {item['issuedefinition']:{'count':0, 'codes':[]} for item in currentlistofdefinitions}
    for thisitem in currentlistofdefinitions:
        thisRound = currentlistofdefinitions_labeled[currentlistofdefinitions_labeled.user_label.apply(lambda x: thisitem['issuedefinition'] in x)]
        rebuildDefinitionCounts[thisitem['issuedefinition']]['count'] +=thisRound.shape[0]
        rebuildDefinitionCounts[thisitem['issuedefinition']]['codes'] = list(thisRound.groupby('user_label_code').size().to_dict().keys())
    


    return rebuildDefinitionCounts

def getrelevantdocuments(getSampleAction, rowsperpage=1, offsetvalue=0):

    db = selectDB(projectselected=getSampleAction['company'])
    engine = db.get_engine() 
    
    if getSampleAction['selected_categories']:
        query = text(f"""
            SELECT DISTINCT ON (user_label) *
            FROM {table_name_labelcandidates}
            WHERE user_label && :user_label
        """)

        with db.engine.connect() as conn:
            result = conn.execute(query, {
                'user_label': [getSampleAction['selected_categories']]  # must be a list of strings
            })

            columns = result.keys()
            thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]

        getSampleAction['selected_categories'] = [i['user_label_code'] for i in thisTexts]
    
    if getSampleAction['selectedaction'] == 'random_sample' and getSampleAction['selected_categories']:
        query = text(f"""
            SELECT * FROM {table_name__master_node_label_candidates}
            WHERE label = ANY(:param) AND method != 'user_manual'
            ORDER BY RANDOM()
            LIMIT {rowsperpage}
        """)
    
    elif getSampleAction['selectedaction'] == 'random_sample' and not getSampleAction['selected_categories']:
        query = text(f"""
            SELECT * FROM {table_name__master_node_label_candidates}
            WHERE method != 'user_manual'
            ORDER BY RANDOM()
            LIMIT {rowsperpage}
        """)
        
    elif getSampleAction['selectedaction'] == 'least_confidence' and getSampleAction['selected_categories']:
        query = text(f"""
            SELECT * FROM {table_name__master_node_label_candidates} 
            WHERE label && :param AND method != 'user_manual'
            ORDER BY confidence ASC  
            LIMIT {rowsperpage} OFFSET {offsetvalue}
        """)   
    
    elif getSampleAction['selectedaction'] == 'least_confidence' and not getSampleAction['selected_categories']:
        query = text(f"""
            SELECT * FROM {table_name__master_node_label_candidates} 
            WHERE method != 'user_manual'
            ORDER BY confidence ASC, id ASC  
            LIMIT {rowsperpage} OFFSET {offsetvalue}
        """) 
        
    else:
        query = text(f"""
            SELECT * FROM {table_name__master_node_label_candidates} 
            WHERE label && :param AND method != 'user_manual'
            LIMIT {rowsperpage} OFFSET {offsetvalue}
        """) 
    
    # Convert Python list into PostgreSQL-compatible array format
    # Convert Python list into PostgreSQL-compatible array format
    if getSampleAction['selectedaction'] == 'search_text':        
        category_condition = "label != ANY(:param)" if getSampleAction['selected_categories_reverse'] else "label = ANY(:param)" 
        if getSampleAction['selected_categories']:
            query = text(f"""
                SELECT * FROM {table_name__master_node_label_candidates} m
                JOIN {table_name_cleantext} c on m.row_hash = c.row_hash
                WHERE 
                    c.clean_text ILIKE :thistext AND 
                    {category_condition}
                    AND m.method != 'user_manual'
                LIMIT {rowsperpage} OFFSET {offsetvalue}
            """)
        else:
            query = text(f"""
                SELECT * FROM {table_name__master_node_label_candidates} m
                JOIN {table_name_cleantext} c on m.row_hash = c.row_hash
                WHERE 
                    c.clean_text ILIKE :thistext
                    AND m.method != 'user_manual'
                LIMIT {rowsperpage} OFFSET {offsetvalue}
            """)        
        # query = text("""
        #     SELECT c.chunk_text AS chunk_text, c.clean_text as clean_text, c.row_hash as row_hash
        #     FROM labelcandidates l
        #     JOIN tokenizeddata t ON l.row_hash_model = t.row_hash_model
        #     JOIN cleandatatext c ON t.row_hash = c.row_hash
        #     WHERE l.row_hash_model IN :hashes
        # """).bindparams(bindparam("hashes", expanding=True))
        
        
        pg_array = "{" + ",".join(f'"{cat}"' for cat in getSampleAction['selected_categories']) + "}"
        params = {
            'thistext': f"%{getSampleAction['text'].strip()}%",
            'param': pg_array
        }
    
    else:
        pg_array = "{" + ",".join(f'"{cat}"' for cat in getSampleAction['selected_categories']) + "}"   
        params = {'param': pg_array}  # Pass formatted array string
    
    with engine.connect() as conn:
        result = conn.execute(query, params)
        columns = result.keys()
        relevantrows = [dict(zip(columns, row)) for row in result.fetchall()]
    
    
    ## get clean text
    if len(relevantrows)==0:
        return relevantrows
    query = text(f"""
        SELECT *
        FROM {table_name_cleantext}
        WHERE row_hash IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))
    
    with engine.connect() as conn:
        result = conn.execute(query, {'hashes': [i['row_hash'] for i in relevantrows]})
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]
        
    
    thisTexts_dict = {items['row_hash']:items for items in thisTexts} 
    for itemsIter in relevantrows:itemsIter.update(thisTexts_dict[itemsIter['row_hash']])
    
    query = text(f"""
        SELECT *
        FROM {table_name_rawtext}
        WHERE row_hash IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))
    
    with engine.connect() as conn:
        result = conn.execute(query, {'hashes': [i['docid'] for i in relevantrows]})
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]
    
    thisTexts_dict = {items['row_hash']:items for items in thisTexts} 
    
    desired_keys = ['docid', 'Body']
    for itemsIter in relevantrows:
        original_dict = thisTexts_dict[itemsIter['docid']]
        subset = {k: original_dict[k] for k in desired_keys if k in original_dict}
        itemsIter.update(subset)
    


    query = text(f"""
        SELECT DISTINCT ON (user_label_code) *
        FROM {table_name_labelcandidates}
        WHERE user_label_code IN :label
        ORDER BY user_label_code, id
    """).bindparams(bindparam("label", expanding=True))

    with engine.connect() as conn:
        result = conn.execute(query, {'label': [i['label'] for i in relevantrows]})
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]

    label_mapping = {i['user_label_code']:i['user_label'] for i in thisTexts}
    for items in relevantrows:
        items['user_label_name']=label_mapping[items['label']]




    return relevantrows



def reassignlabelUser(labelreassignmessage):
    db = selectDB(projectselected=labelreassignmessage['company'])
    restructuredLabelstodb = [{'row_hash':i['row_hash'], 'row_hash_model':i['row_hash_model'], 'user_reassign':i['multilabels'], 'confidence':1} for i in labelreassignmessage['reassignlabels']]
    
    query = text(f"""
        SELECT DISTINCT ON (user_label_code) *
        FROM {table_name_labelcandidates}
    """)

    with db.engine.connect() as conn:
        result = conn.execute(query)
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]

    labelmapping = {frozenset(i['user_label']):i['user_label_code'] for i in thisTexts}

    for items in restructuredLabelstodb:
        items['user_reassign'] = labelmapping[frozenset(items['user_reassign'])]


    # Prepare your parameters
    params = {
        "row_hash_list": tuple([i['row_hash'] for i in labelreassignmessage['reassignlabels']]),
        "row_hash_model_list": tuple([i['row_hash_model'] for i in labelreassignmessage['reassignlabels']]),
    }
    
    # Use correct SQL syntax with tuple binding
    query = text(f"""
        SELECT * FROM {table_name__master_node_label_candidates} 
        WHERE 
            row_hash IN :row_hash_list AND row_hash_model IN :row_hash_model_list
    """)
    
    # Execute and fetch
    with db.engine.connect() as conn:
        result = conn.execute(query, params)
        columns = result.keys()
        relevantrows = [dict(zip(columns, row)) for row in result.fetchall()]
    
    df = pd.DataFrame(relevantrows).drop(columns=['confidence', 'user_reassign'])
    df = df.merge(pd.DataFrame(restructuredLabelstodb), how='left', on=['row_hash', 'row_hash_model'])
    
    row_to_insert = df.to_dict(orient='records')
    
    db.insert_into_table(
        table_name=table_name__master_node_label_candidates,
        rows=row_to_insert,
        where_flag=True,
        conflict_key="row_hash",
        do_update=True,
        batch_size=500
    )

   
    return GetRejectionStats(db)
    
def GetRejectionStats(labelreassignmessage):
    db = selectDB(projectselected=labelreassignmessage['company'])
    
    # Count of rows where user_reassign is not null
    query_total_reassigned = text(f"""
        SELECT COUNT(*)
        FROM {table_name__master_node_label_candidates}
        WHERE user_reassign IS NOT NULL
    """)
    
    # Count of rows where user_reassign is not null AND label != user_reassign
    query_mismatched = text(f"""
        SELECT COUNT(*)
        FROM {table_name__master_node_label_candidates}
        WHERE user_reassign IS NOT NULL AND label != user_reassign
    """)
    
    with db.engine.connect() as conn:
        total_reassigned = conn.execute(query_total_reassigned).scalar()
        mismatched_reassigned = conn.execute(query_mismatched).scalar()   

    return {'total_reassigned':total_reassigned, 'mismatched_reassigned':mismatched_reassigned}

def assignNewUserLabel(userLabelRequest):

    db = selectDB(projectselected=userLabelRequest['company'])


    query = text(f"""
        SELECT *
        FROM {table_name_labelcandidates} 
        WHERE row_hash_model IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))

    with db.engine.connect() as conn:
        result = conn.execute(query, {'hashes': [userLabelRequest['row_hash_model']]})
        column_names = result.keys()
        entireTexts = result.fetchall()




    column_names = list(result.keys())
    idx = column_names.index('user_label')

    entireTexts_addlabel = []
    for row in entireTexts:
        row_list = list(row)
        row_list[idx] = userLabelRequest['user_label']
        entireTexts_addlabel.append(tuple(row_list))

    db.insert_into_table(
        table_name=table_name_labelcandidates,
        rows=entireTexts_addlabel,
        conflict_key="row_hash_model",
        do_update=True,
        batch_size=500
    )    
    
    return True

def getPossibleMisLabels(labelreassignmessage):
    selected_db = selectDB(projectselected=labelreassignmessage['company']) 

    query = f"""SELECT * 
                FROM {table_name_labelcandidates_validation}
                WHERE matching_labels IS TRUE """

    with selected_db.engine.begin() as conn:
        returnedValues = conn.execute(text(query))
        columns = returnedValues.keys()
        relevantrows = [dict(zip(columns, row)) for row in returnedValues.fetchall()]    
    relevantrows = sorted(relevantrows, key=lambda x: x['similarity'], reverse=True)
    relevantrows_df = pd.DataFrame(relevantrows)
    
    if relevantrows_df.shape[0]<1:return False
    
    row_hashes = list(set(relevantrows_df.source_row_hash.to_list()))

    query = text(f"""
        SELECT DISTINCT c.clean_text as clean_text, l.source_row_hash as source_row_hash
        FROM {table_name_labelcandidates_validation} l
        JOIN {table_name_tokenize} t ON l.source_row_hash = t.row_hash
        JOIN {table_name_cleantext} c ON t.row_hash = c.row_hash
        WHERE l.source_row_hash IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))

    with selected_db.engine.connect() as conn:
        entireTexts = conn.execute(query, {'hashes': row_hashes})
        columns = entireTexts.keys()
        entireTexts = [dict(zip(columns, row)) for row in entireTexts.fetchall()]     
    relevantrows_df = relevantrows_df.merge(pd.DataFrame(entireTexts), how='left', on='source_row_hash')
    relevantrows_df = relevantrows_df.rename(columns={'clean_text':'source_clean_text'})


    row_hashes = list(set(relevantrows_df.target_row_hash.to_list()))

    query = text(f"""
        SELECT DISTINCT c.clean_text as clean_text, l.target_row_hash as target_row_hash
        FROM {table_name_labelcandidates_validation} l
        JOIN {table_name_tokenize} t ON l.target_row_hash = t.row_hash
        JOIN {table_name_cleantext} c ON t.row_hash = c.row_hash
        WHERE l.target_row_hash IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))

    with selected_db.engine.connect() as conn:
        entireTexts = conn.execute(query, {'hashes': row_hashes})
        columns = entireTexts.keys()
        entireTexts = [dict(zip(columns, row)) for row in entireTexts.fetchall()]     
    relevantrows_df = relevantrows_df.merge(pd.DataFrame(entireTexts), how='left', on='target_row_hash')
    relevantrows_df = relevantrows_df.rename(columns={'clean_text':'target_clean_text'})
    #relevantrows_df = relevantrows_df.drop(columns=['row_hash', 'matching_labels'])

    return relevantrows_df.to_dict('records')

def func_defineLabelingasComplete(request_json):

    selected_db = selectDB(projectselected=request_json['company']) 
    value_to_insert = "USERLABELEDNODES"

    
    
    stmt = insert(selected_db.tables[progress_table_name]).values(status_text=value_to_insert).on_conflict_do_nothing()

    with selected_db.engine.begin() as conn:
        conn.execute(stmt)
    
    print('Marked Stage as Complete')
    return True


def getReviewedStats(projectselected):

    selected_db = selectDB(projectselected=projectselected) 
    # 1 number of documents ingested as raw text
    query_entire = f"""
        SELECT COUNT(DISTINCT docid)
        FROM rawdatatext    
    """
    with selected_db.engine.connect() as conn:
        result = conn.execute(text(query_entire)).scalar()

    numberofdocumentsIngested = result


    query_entire = f"""
        SELECT *
        FROM {table_name_masterLabels}
    """

    with selected_db.engine.connect() as conn:
        result = conn.execute(text(query_entire))
        columns = result.keys()  # get column names
        result_df = pd.DataFrame(result.fetchall(), columns=columns)

    result_df['Results'] = result_df.user_reassign==result_df.label


    query = text(f"""
        SELECT DISTINCT ON (user_label_code) *
        FROM {table_name_labelcandidates}
    """)

    with selected_db.engine.connect() as conn:
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

def getTableofDocumentsProgress(projectselected):
    selected_db = selectDB(projectselected=projectselected) 

    query_entire = f"""
        SELECT r.docid AS docid, m.row_hash as row_hash, m.label as label, m.user_reassign as user_reassign, m.confidence as confidence
        FROM {table_name_masterLabels} m 
        JOIN {table_name_cleantext} c ON m.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """

    with selected_db.engine.connect() as conn:
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

    with selected_db.engine.connect() as conn:
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

    with selected_db.engine.connect() as conn:
        result = conn.execute(query)
        columns = result.keys()
        thisTexts = [dict(zip(columns, row)) for row in result.fetchall()]

    labelmapping = {i['user_label_code']:list(frozenset(i['user_label'])) for i in thisTexts}

    labelmapping = {i:' '.join(labelmapping[i])[:3] for i in listofcolumns}
    label_dist = label_dist.rename(columns=labelmapping)
    label_dist['most_frequent'] = label_dist['most_frequent'].map(labelmapping)
    label_dist['user_reassign'] = label_dist['user_reassign'].map(labelmapping)
    label_dist = label_dist.rename(columns={'most_frequent':'Propogated Label', 'user_reassign':'User Label', 'label_entropy':'Entropy'})
    label_dist['Entropy'] = label_dist['Entropy'].apply(lambda x:round(x,2))
    label_dist = label_dist.reset_index()
    
    return {'columns':list(label_dist.columns), 
            'rows':label_dist.replace({np.nan: None, np.inf: None, -np.inf: None}).to_dict('records')}


def initializeDBNames():

    selected_db = DatabaseManager(db_name=os.environ.get("DB_NAME"))

    # Regular connection to list existing databases
    with selected_db.engine.connect() as conn:
        result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        databases = [row[0] for row in result]

    # Create new engine with AUTOCOMMIT enabled
    autocommit_engine = selected_db.engine.execution_options(isolation_level="AUTOCOMMIT")

    for requiredDB in ['currentproject', 'db_test']:
        if requiredDB not in databases:
            with autocommit_engine.connect() as conn:
                conn.execute(text(f'CREATE DATABASE "{requiredDB}"'))

    with selected_db.engine.connect() as conn:
        result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        databases_secondround = [row[0] for row in result]        

    allPossibleDataBases = ['currentproject', 'db_test']

    existingdatabases = set(databases_secondround)&set(allPossibleDataBases)

    MenuComponentText = {
    'currentproject':{'ListSubheader':'Current Project', 'menu_value':'current-project', 'primaryText':'Current Workload', 'secondaryText':'Load Data'},
    'db_test':{'ListSubheader':'In Progress', 'menu_value':'demo-live', 'primaryText':'In Progress', 'secondaryText':'Live Demonstration'},

    }
    menuContents = {'demo': [],
                   'current-project':[]}      


    for thisdb in existingdatabases:
        if thisdb == 'currentproject':
            menuContents['current-project'].append(MenuComponentText[thisdb])
        else:
            menuContents['demo'].append(MenuComponentText[thisdb])        

    return menuContents  

def runControlSwitch(company, userinjesttype=''):

    selected_db = selectDB(projectselected=company)
    controllingcontainer_switch.runworkerjobs(db=selected_db, bucketname=selectionmap[company]['bucket'], userinjesttype=userinjesttype) 
    
    return True

def runControlSwitch_async(company, userinjesttype=''):
    threading.Thread(target=runControlSwitch, args=(company, userinjesttype,), daemon=True).start()
    
    
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'secret'  # for session signing
app.config['SESSION_TYPE'] = 'filesystem'  # store sessions in temp dir
Session(app)

# Main entry point
# Define your endpoints
@app.route('/api/', methods=['GET', 'POST'])
def handle_request():
    global naicsindexselection
    """HTTP Cloud Function."""
    request_json = request.get_json(silent=True)
    request_args = request.args


    return jsonify(get_topicdefinitions(request_json))
    # Implement your request handling logic
    return request_args 
    
@app.route('/api/jobcompleted', methods=['POST'])
def ListeningForJobCompletion():
    request_json = request.get_json(silent=True)
    db_name = request_json['db_name']
    ## convert db name back to company/project name
    for company, records in selectionmap.items():
        if records['db_name']==db_name:break
    
    print('recieved job completion report, starting control switch')    
    runControlSwitch_async(company)

    return jsonify({"status": "Message Recieved, job completion report"}), 200
    
@app.route('/api/dbselection', methods=['POST'])
def DataBaseSelection():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if company =='':
        menueContent = initializeDBNames()
        return jsonify({"status": "db cached", "company": company, "menueContent":menueContent}), 200
        
    else:
        selected_db = selectDB(projectselected=company)  # store it
        return jsonify({"status": "db cached", "company": company}), 200
#    session['selected_company'] = company  # store in session
    return jsonify({"error": "no company selected"}), 400

@app.route('/api/getcurrentprogress', methods=['POST'])
def GetCurrentProgress():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400
    print('GetCurrentProgress')
    print(company)
    
    if 'progresstype' in request_json:
        match request_json['progresstype']:
            case 'overall':
                print(request_json['progresstype'])
                data = getdocumentsLabeledProgress(projectselected=company)
            case 'reviewedstats':
                data = getReviewedStats(projectselected=company)
            case 'listofpropogateddocuments':
                data = getTableofDocumentsProgress(projectselected=company)
    
    else:
        data = getcurrentprogress(projectselected=company)
    if not data:
        return jsonify({"error": "database for project not found"}), 400
        
    return jsonify({"status": "ok", "data": data}), 200

@app.route('/api/getitemsinbucket', methods=['POST'])
def GetItemsinBucket():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    userinjesttype = request_json['userinjesttype'] 
    data=None
    if not company:
        return jsonify({"error": "no company selected"}), 400

    try:
        data = getitemsinstorage(projectselected=company)
        if userinjesttype!='' and data is not None:
            runControlSwitch_async(company, userinjesttype)
    except:return jsonify({"error": "database for project not found"}), 400
        
    return jsonify({"status": "ok", "data": data}), 200
    

@app.route('/api/addcategory', methods=['POST'])
def AddCategory():
    request_json = request.get_json(silent=True)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400

    print(request_json)
    currentlistofdefinitions = addnewdefinitiontotable(request_json)
    return jsonify({"status": "ok", "data": currentlistofdefinitions}), 200    

@app.route('/api/getnextcandidatelabel', methods=['POST'])
def GetNextCandidateLabel():
    request_json = request.get_json(silent=True)
    print(request_json)
    
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400

    if request_json['markstagecomplete']=='complete':
        print('Yes Yes')
        func_defineLabelingasComplete(request_json)
        runControlSwitch_async(company)
        return jsonify({"status": "ok", "data": ""}), 200
    
    textforcandidates = getNextLabelCandidate(request_json)
    return jsonify({"status": "ok", "data": textforcandidates}), 200

@app.route('/api/getnextnearduplicate', methods=['POST'])
def GetNextNearDuplicate():
    request_json = request.get_json(silent=True)
    print(request_json)
    company = request_json['company']
    if not company:
        return jsonify({"error": "no company selected"}), 400
        
    textfornearduplicatecandidates = get_candidate_sample(lo=request_json["lo"], hi=request_json["hi"], last_answer=request_json["last_answer"], projectselected=company, tolerance=0.005, percent_quantile=0.99)

    return jsonify({"status": "ok", "data": textfornearduplicatecandidates}), 200

@app.route('/api/action', methods=['POST'])
def respondtoindexquery():

    request_json = request.get_json(silent=True)
    print(request_json)
    if not request_json or any([i in request_json for i in ['random_sample' , 'least_confidence', 'search_text']]):
        return jsonify({"error": "Select atleast one category to sample"}), 400

    print('Returning Response of index search')

    ### if label reassignment is in this message, then do a label reassign
    rejectionStats=None
    if 'reassignlabels' in request_json:
        if request_json['reassignlabels']:
            rejectionStats = reassignlabelUser(request_json)
        else:
            rejectionStats = GetRejectionStats(request_json)
     
    print('rejectionStats')
    print(rejectionStats)
    rowsperpage=1
    offsetvalue = max([0,request_json['page']-1])*rowsperpage
    print('offsetvalue', offsetvalue)
    relevantRows = getrelevantdocuments(request_json, rowsperpage=rowsperpage, offsetvalue=offsetvalue)
    
    return jsonify({'data':relevantRows, 'rejectionStats':rejectionStats})

@app.route('/api/labelthiscandidate', methods=['POST'])
def GetUserLabel():

    request_json = request.get_json(silent=True)

    print('label assignment by user')    
    assignment = assignNewUserLabel(request_json)
    possibleMisMatch=[]
    if ENABLELABELCHECK=='True':
        possibleMisMatch = getPossibleMisLabels(request_json)
    
    if assignment:
        return jsonify({"status": "ok", "data": request_json, 'mismatch':possibleMisMatch}), 200
    else:
        return jsonify({"error": "Could Not Assign Label"}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)