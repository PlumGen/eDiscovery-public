import os
import pandas as pd

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
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

table_name_prepropogationtable = os.environ.get("PREPROPOGATEDLABELS")

table_name_masterLabels    = os.environ.get("MASTERNODELABELS")

chunksize  = os.environ.get("CHUNKSIZEDBTOCONTAINER", 500)


from sqlalchemy import inspect
from database_manager import DatabaseManager
import os
from sqlalchemy import Table, Column, text, String, select, inspect, func

db = DatabaseManager()


engine = db.get_engine()

inspector = inspect(engine)
tables = inspector.get_table_names()
print(tables)

db.create_schema_and_indexes()




with db.conn_read() as conn:
    result = conn.execute(
        select(func.count(func.distinct(db.tables[table_name_cleantext].c.docid)))
    ).scalar()

totalNumberofDocuments = result

with db.conn_read() as conn:
    result = conn.execute(
        select(func.count()).select_from(db.tables[table_name_cleantext])
    ).scalar()

totalNumberofPages = result

with db.conn_read() as conn:
    result = conn.execute(
        select(func.count()).select_from(db.tables[table_name_ranking])
    ).scalar()

totalRankedPages = result


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
user_manual = Master_df[Master_df.method=='user_manual'].shape[0]
bins = [0, 0.75, 0.80, 0.85, 0.90, 0.95, 1]  # your list of threshold values
counts = pd.cut(Master_df['confidence'], bins=bins, include_lowest=True).value_counts().sort_index()


print(f'Number of Documents: {totalNumberofDocuments}')
print(f'Number of Pages: {totalNumberofPages}')
print(f'Number of Ranked Pages: {totalRankedPages}')
print(f'Number of User Manually Labeled: {user_manual}')
print(f'Total Nodes Propogated: {counts.sum()}')

print(f'Confidence Levels: {counts}')

