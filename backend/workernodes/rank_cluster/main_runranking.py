
from sqlalchemy import Column 
from sqlalchemy import String, Integer, Float
from sqlalchemy import create_engine, text, MetaData, Table, inspect, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import ProgrammingError
from .samples_deter_GPU import createdeterministicRanking

import pandas as pd
import numpy as np
import os

import json
import faiss


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)

table_name_ranking = os.environ.get("RANKINGDATATEXTTABLE")
table_name_markedduplicates = os.environ.get("MARKEDDUPLICATESTEXTTABLE")
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
table_name_embed = os.environ.get("EMBEDDATATEXTTABLE")

chunksize = int(os.environ.get("CHUNKSIZEDBTOCONTAINER"))
embed_col=os.environ.get("EMBEDCOLUMNS")

rankingword_countThresh = int(os.environ.get("RANKWORDCOUNTTHRESHOLD"))
rankingword_alphanumericThresh = float(os.environ.get("ALPHANUMERICRATIO"))
rankingword_completesentences = int(os.environ.get("NUMCOMPLETESENTENCES"))

mainEmbedModel = str(os.environ.get("MAINEMBEDMODEL"))

def main_runranking(db, RunCheck): 
    engine = db.get_engine()
    progress_table = db.tables[progress_table_name]
    inspector = inspect(engine)

    with db.conn_read() as conn:
        rankingdone = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "RANKINGCOMPLETE")
        ).first() 

    with db.conn_read() as conn:
        duplicatesMarked = conn.execute(
            select(progress_table.c.status_text).where(progress_table.c.status_text == "DUPLICATESMARKEDCOMPLETE")
        ).first() 

    if rankingdone and inspector.has_table(table_name_ranking):
        print("RANKINGCOMPLETE already exists in progress table.")
        return
    
    if not (duplicatesMarked and inspector.has_table(table_name_markedduplicates)):
        print("Cannot continue with Ranking since duplicates are not marked yet")
        return
    
    print("RANKINGCOMPLETE not found.")
    # --- get distinct model_names from embed table ---
    with db.conn_read() as conn:
        model_names = [r[0] for r in conn.execute(
            text(f"SELECT DISTINCT model_name FROM {table_name_embed}")
        ).fetchall()]




    for model_name in model_names:
        ### check which models still need to be processed
        with db.conn_read() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(DISTINCT e.row_hash_model)
                FROM {table_name_embed} e
                LEFT JOIN {table_name_markedduplicates} m
                ON e.row_hash = m.row_hash
                WHERE e.wordcount >= :wordthresh
                AND e.alphanumeric >= :alphathresh
                AND e.num_sentences >= :numsentencethresh
                AND COALESCE(m.role, 'none') != 'child'
                AND e.model_name = :modelname
                
            """), {
                "wordthresh": rankingword_countThresh,
                "alphathresh": rankingword_alphanumericThresh,
                "numsentencethresh": rankingword_completesentences,
                "modelname": model_name
            })
            unique_count = result.scalar()

        with db.conn_read() as conn:
            result = conn.execute(text(f"""
                SELECT COUNT(DISTINCT row_hash_model)
                FROM {table_name_ranking}
                WHERE model_name = :modelname
            """), {"modelname": model_name
            })
            rankedrows = result.scalar()

        if rankedrows==unique_count:
            print(f"Skipping model as it is complete: {model_name}")        
            continue
            
        print(f"Processing model: {model_name}")

        query = f"""
            SELECT id, * 
            FROM {table_name_embed}
            WHERE wordcount >= {rankingword_countThresh}
              AND alphanumeric >= {rankingword_alphanumericThresh}
              AND num_sentences >= {rankingword_completesentences}
              AND model_name = '{model_name}'
        """
        listofDfs = []
        for df in db.resilient_read_query_keyset(query, chunksize=chunksize):
            listofDfs.append(df)
        if not listofDfs:
            continue
        df_embed = pd.concat(listofDfs)

        query = f"SELECT id, * FROM {table_name_markedduplicates} WHERE role = 'child'"
        listofDfs = []
        with db.conn_read() as conn:
            for df in pd.read_sql(query, conn, chunksize=chunksize):
                listofDfs.append(df)
        Child_df = pd.concat(listofDfs)

        df_embed = df_embed[~df_embed.row_hash.isin(Child_df.row_hash)]

        df_embed_ranked = createdeterministicRanking(df_embed, RunCheck, embed_col)
        df_embed_ranked['Selection_Distance'] = 1 - df_embed_ranked.Selection_Distance
        df_embed_ranked['Selection_Distance'] = df_embed_ranked.Selection_Distance.replace(1, 0)

        df_embed_ranked = df_embed_ranked[['row_hash', 'row_hash_model', 'model_name', 
                                           'Selection_Rank_Deterministic', 'Selection_Distance']]

        rows_to_insert = df_embed_ranked.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name_ranking,
            rows=rows_to_insert,
            conflict_key="row_hash_model",
            do_update=False,
            batch_size=500
        )

        print(f"Injected rankings for model {model_name} into '{table_name_ranking}'.")

    # --- verify completeness ---
    with db.conn_read() as conn:
        result = conn.execute(text(f"""
            SELECT COUNT(DISTINCT e.row_hash_model)
            FROM {table_name_embed} e
            LEFT JOIN {table_name_markedduplicates} m
            ON e.row_hash = m.row_hash
            WHERE e.wordcount >= :wordthresh
            AND e.alphanumeric >= :alphathresh
            AND e.num_sentences >= :numsentencethresh
            AND COALESCE(m.role, 'none') != 'child'
        """), {
            "wordthresh": rankingword_countThresh,
            "alphathresh": rankingword_alphanumericThresh,
            "numsentencethresh": rankingword_completesentences
        })
        unique_count = result.scalar()

    with db.conn_read() as conn:
        result = conn.execute(text(f"""
            SELECT COUNT(DISTINCT row_hash_model)
            FROM {table_name_ranking}
        """))
        rankedrows = result.scalar()

    print(f"Number of rows meeting threshold: {unique_count}")
    print(f"Number of unique ranked rows: {rankedrows}")

    if rankedrows == unique_count:
        stmt = insert(progress_table).values(status_text="RANKINGCOMPLETE").on_conflict_do_nothing()
        with db.conn_tx() as conn:
            conn.execute(stmt)
        print("Ranking marked stage as complete.")
