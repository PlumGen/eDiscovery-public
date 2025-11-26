import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message="A value is trying to be set on a copy")

import pandas as pd
from sqlalchemy import text
import os
import masternodes.taskManager as taskManager
from sqlalchemy import bindparam
from itertools import chain

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    

table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")
table_name_rankingtable = os.environ.get("RANKINGDATATEXTTABLE")

chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))

embed_col=os.environ.get("EMBEDCOLUMNS")
block_size=int(os.environ.get("FAISSKSEARCHES"))

table_name_tokenize  = os.environ.get("TOKENIZEDATATEXTTABLE")


table_name_disambiguationtable = os.environ.get("DISAMBIGUATIONLABELS")

excludeLabelConfidenceLevels = float(os.environ.get("EXCLUDELABELCONFIDENCELEVELS"))
table_name_deduplicates = os.environ.get("MARKEDDUPLICATESTEXTTABLE")

def getLabeledNodes(db=None, table_name_masterLabels=table_name_masterLabels, excludeLabelConfidenceLevels=excludeLabelConfidenceLevels):

    subquery = f"""
    SELECT id
    FROM (
        SELECT id, row_hash, confidence,
            ROW_NUMBER() OVER (PARTITION BY row_hash ORDER BY confidence DESC, id) AS rank
        FROM {table_name_masterLabels}
    ) sub
    WHERE rank = 1
    """

    query = f"""
    SELECT *
    FROM {table_name_masterLabels}
    WHERE id IN ({subquery})
    """

    list_rank_df = []
    for df in db.resilient_read_query_keyset(query, key_column='id', chunksize=chunksize):
        list_rank_df.append(df)
    Master_df = pd.concat(list_rank_df)
    
    print(f'Downloaded Labeled Nodes: {Master_df.shape[0]}')
    # reconstructMasters=[]
    # for methods in set(Master_df.method):
        # temp = Master_df[Master_df.method==methods]
        # temp = temp[temp.confidence>=temp.confidence.quantile(excludeLabelConfidenceLevels)]
        # reconstructMasters.append(temp)
        
    # Master_df = pd.concat(reconstructMasters)
    Master_df = Master_df[Master_df.confidence>=Master_df.confidence.quantile(excludeLabelConfidenceLevels)]
    print(f'Downloaded Labeled Nodes Meeting Confidence Level: {Master_df.shape[0]}')
        
    Master_df = Master_df.rename(columns={'label':'user_label_actual'})
    Master_df['user_label_standard'] = Master_df['user_label_actual']
    
    return Master_df.drop(columns='row_hash_model')

def getRankingTable(model_name, db):
    
    query = f"SELECT * FROM {table_name_rankingtable} WHERE model_name = '{model_name}'"

    listofDfs = []
    # with engine.connect() as conn:
    for df in db.resilient_read_query_keyset(query, chunksize=chunksize):listofDfs.append(df)

        ### the rest of the code below could be run under this loop if the nodes are too large
    df = pd.concat(listofDfs)
    df = df.reset_index(drop=True)

    return df #.drop(columns=['row_hash_model'], errors='ignore')
    
                    

def getRelevantEmbeds(df_Save, db=None, table_name_tokenize=table_name_tokenize, table_name_embed=table_name_embed, model_name=None):

    listofhashes = tuple(df_Save.row_hash_model.unique())

    query = text(f"""
        SELECT row_hash, row_hash_model, embed FROM {table_name_embed}
        WHERE model_name = :model_name AND
        row_hash_model IN :hashes
    """).bindparams(bindparam("hashes", expanding=True))

    with db.conn_read() as conn:
        df_embed = pd.read_sql_query(query, conn, params={"model_name": model_name, "hashes": listofhashes})
   
    return df_embed


def getDuplicateRows(db, model_name):

    query_entire = f"""
        SELECT DISTINCT e.row_hash, e.row_hash_model  
        FROM {table_name_deduplicates} d 
        JOIN {table_name_embed} e ON d.row_hash = e.row_hash  
        WHERE d.role = 'child'
        AND e.model_name='{model_name}'
    """
    
    with db.conn_read() as conn:
        result = conn.execute(text(query_entire)).fetchall()

    return set((i[0], i[1]) for i in result)
    

def getUnrankedRows(db, model_name):

    query_entire = f"""
        SELECT DISTINCT e.row_hash, e.row_hash_model
        FROM {table_name_embed} e
        LEFT JOIN {table_name_rankingtable} r 
        ON e.row_hash_model = r.row_hash_model
        LEFT JOIN {table_name_deduplicates} d 
        ON e.row_hash = d.row_hash
        WHERE e.model_name = '{model_name}'
        AND r.row_hash_model IS NULL
        AND d.row_hash IS NULL
    """
    with db.conn_read() as conn:
        result = conn.execute(text(query_entire)).fetchall()
        
    return set((i[0], i[1]) for i in result)


def addAdditionalRowsAddOps(db, additional_flat_list, df_Save, model_name):
    addtheseRows = set()
    for ops in additional_flat_list:
        if ops=='IncludeDuplicates':
            addtheseRows.update(getDuplicateRows(db, model_name))
        if ops=='IncludeUnRanked':
            addtheseRows.update(getUnrankedRows(db, model_name))
    

    addtheseRows = list(addtheseRows-set(df_Save.apply(lambda x: frozenset([x['row_hash'], x['row_hash_model']]), axis=1).tolist()))
    
    template = df_Save.iloc[-1]
    template_list=[]
    for i in addtheseRows:
        temp = template.copy()
        temp['row_hash'] = i[0]
        temp['row_hash_model'] = i[1]
        template_list.append(temp.to_dict())

    Additional_Rows = pd.DataFrame(template_list)  
    
    df_Save = pd.concat([df_Save, Additional_Rows])
    return df_Save

def min_max_normalize(values):
    values = [float(i) for i in values]
    min_val = min(values)
    max_val = max(values)
    if max_val == min_val:
        return [0.0 for _ in values]  # avoid divide by zero
    return [(x - min_val) / (max_val - min_val) for x in values]

def reconstructAmbiguousDF(Ambiguous_df):
    Ambiguous_df['category_reassign_l1_distance_normed'] = Ambiguous_df.category_reassign_l1_distance.apply(min_max_normalize)
    maximumSourcestoKeep = int(Ambiguous_df.category_reassign_l1_confidence.apply(len).max())
    
    cols = [
        "row_hash",
        "category_reassign_l1_source",
        "category_reassign_l1",
        "category_reassign_l1_distance_normed",
        "category_reassign_l1_confidence",
        "category_reassign_l1_distance",
        "model_votes",
    ]

    # Step 1: Keep only rows with max model_votes per row_hash
    max_votes = Ambiguous_df.groupby("row_hash")["model_votes"].transform("max")
    df = Ambiguous_df[Ambiguous_df["model_votes"] == max_votes][cols].copy()

    # Step 2: Explode list-like columns
    to_explode = [
        "category_reassign_l1_source",
        "category_reassign_l1",
        "category_reassign_l1_distance_normed",
        "category_reassign_l1_confidence",
        "category_reassign_l1_distance",
    ]
    df = df.explode(to_explode, ignore_index=True)

    # Step 3: Cast numeric fields
    df["category_reassign_l1_distance_normed"] = df["category_reassign_l1_distance_normed"].astype(float)
    df["category_reassign_l1_confidence"] = df["category_reassign_l1_confidence"].astype(float)
    df["category_reassign_l1_distance"] = df["category_reassign_l1_distance"].astype(float)

    # Step 4: Sort within each row_hash
    df = df.sort_values(
        ["category_reassign_l1_distance_normed", "category_reassign_l1_confidence"],
        ascending=[False, False]
    )

    # Step 5: Drop duplicates per row_hash+source, keep best
    df = df.drop_duplicates(subset=["row_hash", "category_reassign_l1_source"], keep="first")

    # Step 6: Group back to dict list
    final_dict_list = (
        df.groupby("row_hash")
        .apply(lambda g: {
            "row_hash": g.name,
            "category_reassign_l1_source": g["category_reassign_l1_source"].tolist()[:maximumSourcestoKeep],
            "category_reassign_l1": g["category_reassign_l1"].tolist()[:maximumSourcestoKeep],
            "category_reassign_l1_distance_normed": g["category_reassign_l1_distance_normed"].tolist()[:maximumSourcestoKeep],
            "category_reassign_l1_confidence": g["category_reassign_l1_confidence"].tolist()[:maximumSourcestoKeep],
            "category_reassign_l1_distance": g["category_reassign_l1_distance"].tolist()[:maximumSourcestoKeep],
        })
        .tolist()
    )

    Ambiguous_df = Ambiguous_df.sort_values(by='model_votes').drop_duplicates(subset='row_hash', keep='last')   
    Ambiguous_df['user_label_standard'] = Ambiguous_df.user_label_standard_frozen

    Ambiguous_df = Ambiguous_df[[
     'row_hash',
     'confidence',
     'created_at',
     'lowest_difference',
     'model_votes',
     'row_hash_model',
     'timestamp',
     'updated_at',
     'user_label_standard',
     'user_label_standard_frozen']].merge(pd.DataFrame(final_dict_list), how='left', on='row_hash')
    
    return Ambiguous_df.drop(columns='category_reassign_l1_distance_normed')
    
def getDisambig(db, Save_df, Master_df):    
    
    engine = db.get_engine()
    
    ambiguousset_tablename = os.environ.get("AMBIGUOUSSETTABLE")

    query = f"""SELECT *
    FROM {ambiguousset_tablename}
    """

    list_label_df=[]
    with db.conn_read() as conn:
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):list_label_df.append(df)
    Ambiguous_df = pd.concat(list_label_df)

    Ambiguous_df = Ambiguous_df.sort_values(by='confidence').drop_duplicates(subset=['row_hash', 'row_hash_model'], keep='last')
    Ambiguous_df['user_label_standard_frozen'] = Ambiguous_df.user_label_standard_frozen.apply(frozenset)

    temp = pd.DataFrame(Ambiguous_df.groupby(by=['row_hash', 'user_label_standard_frozen']).size())
    temp = temp.reset_index() 
    temp.columns = ['row_hash', 'user_label_standard_frozen', 'model_votes']
    Ambiguous_df = Ambiguous_df.merge(temp, how='left', on=['row_hash', 'user_label_standard_frozen'])
    Ambiguous_df = Ambiguous_df.drop(columns='id')
    
    Ambiguous_df = reconstructAmbiguousDF(Ambiguous_df)

    Ambiguous_df = Ambiguous_df[~Ambiguous_df.row_hash.isin(Master_df.row_hash)]
    Ambiguous_df = Ambiguous_df.drop(columns=['row_hash_model'])
    Ambiguous_df = Ambiguous_df.merge(Save_df, how='left', on=['row_hash'])
    
    Ambiguous_df = Ambiguous_df.rename(columns={'category_reassign_l1':'Category_Reassign_L1'})
    Ambiguous_df = Ambiguous_df.rename(columns={'category_reassign_l1_source':'Category_Reassign_L1_Source'})
    Ambiguous_df = Ambiguous_df.rename(columns={'category_reassign_l1_distance':'Category_Reassign_L1_distance'})

    return Ambiguous_df
    
def selectModel(model_name, db, disAmbig=False):

    df_Save = getRankingTable(model_name, db)
    additional_flat_list = taskManager.checkforcurrentAdditOps(db)
    if additional_flat_list:
        df_Save = addAdditionalRowsAddOps(db, additional_flat_list, df_Save, model_name)
    
    embed_df = getRelevantEmbeds(df_Save, db, model_name=model_name)

    df_Save = df_Save[['row_hash', 'row_hash_model', 'Selection_Rank_Deterministic', 'Selection_Distance']].merge(embed_df[['row_hash', 'row_hash_model', 'embed']], how='left', on=['row_hash', 'row_hash_model'])
    df_Save['disambigcycles'] = 0

    Master_df = getLabeledNodes(db=db, table_name_masterLabels=table_name_masterLabels)

    Master_df = Master_df.merge(df_Save[['row_hash', 'row_hash_model', 'embed', 'Selection_Rank_Deterministic', 'disambigcycles']], how='left', on=['row_hash'])
    
    if disAmbig:
        Ambiguous_df = getDisambig(db, df_Save, Master_df)

        flat_list = list(set(chain.from_iterable(Ambiguous_df.Category_Reassign_L1_Source.to_list())))
        flat_list = set(flat_list) - set(Master_df.row_hash.to_list())
        Ambiguous_df = Ambiguous_df[~Ambiguous_df.Category_Reassign_L1_Source.apply(lambda x: any([i in flat_list for i in x]))]
        
        return Master_df.drop_duplicates(subset='row_hash'), Ambiguous_df.drop_duplicates(subset='row_hash')
    return Master_df.drop_duplicates(subset='row_hash'), df_Save.drop_duplicates(subset='row_hash')
