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
    

def getdocumentsLabeledProgress(selected_db):

    # --- FIX SQL JOINS (use r.docid = c.docid everywhere) ---
    query_prepared = f"""
        SELECT 
            r.docid AS baseID,
            e.row_hash AS row_hash
        FROM {table_name_embed} e
        JOIN {table_name_cleantext} c ON e.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """

    query_dedup = f"""
        SELECT 
            r.docid AS baseID,
            e.row_hash AS row_hash
        FROM {table_name_deduplicates} e
        JOIN {table_name_cleantext} c ON e.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
        WHERE e.role = 'child'
    """

    query_rank = f"""
        SELECT 
            r.docid AS baseID,
            e.row_hash AS row_hash
        FROM {table_name_ranking} e
        JOIN {table_name_cleantext} c ON e.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """

    query_label = f"""
        SELECT 
            r.docid AS baseID,
            e.row_hash AS row_hash
        FROM {table_name_masterLabels} m 
        JOIN {table_name_embed} e ON m.row_hash = e.row_hash
        JOIN {table_name_cleantext} c ON e.row_hash = c.row_hash
        JOIN rawdatatext r ON c.docid = r.row_hash
    """

    # Raw document list
    with selected_db.conn_read() as conn:
        DocumentBaseline = pd.DataFrame(conn.execute(text("SELECT docid AS baseID FROM rawdatatext")).fetchall())

    # Stage dataframes
    with selected_db.conn_read() as conn:
        Prepared_df   = pd.DataFrame(conn.execute(text(query_prepared)).fetchall()).drop_duplicates()
        Deduplicates_df = pd.DataFrame(conn.execute(text(query_dedup)).fetchall()).drop_duplicates()
        Rankings_df   = pd.DataFrame(conn.execute(text(query_rank)).fetchall()).drop_duplicates()
        AnyLabeling_df  = pd.DataFrame(conn.execute(text(query_label)).fetchall()).drop_duplicates()

    # --- BUILD LONG TABLE WITH STAGE FLAGS ---
    Prepared_df["stage"]     = "prepared"
    Deduplicates_df["stage"] = "duplicates"
    Rankings_df["stage"]     = "ranked"
    AnyLabeling_df["stage"]  = "labeled"

    long = pd.concat([Prepared_df, Deduplicates_df, Rankings_df, AnyLabeling_df], ignore_index=True).drop_duplicates()

    # universe of (baseID,row_hash) seen anywhere
    universe = long[["baseid","row_hash"]].drop_duplicates()

    # pivot to wide boolean flags per (baseID,row_hash)
    flags = (
        long.assign(val=True)
            .pivot_table(index=["baseid","row_hash"], columns="stage", values="val", fill_value=False, aggfunc="any")
            .reset_index()
    )

    # --- RE-COMPUTE COUNTS ON CHUNK-LEVEL FLAGS (exclude duplicate chunks from rank/label) ---

    # flags has one row per (baseID,row_hash) with boolean columns: prepared, duplicates, ranked, labeled
    # If you don't have it in scope, rebuild as in the previous step.

    calc = (
        flags.assign(
            processed_chunk=lambda d: d["prepared"],
            dup_chunk=lambda d: d["duplicates"],
            nondup_chunk=lambda d: d["prepared"] & ~d["duplicates"],
            ranked_nondup=lambda d: d["ranked"] & ~d["duplicates"],
            labeled_nondup=lambda d: d["labeled"] & ~d["duplicates"],
        )
        .groupby("baseid", as_index=False)
        .agg(
            processed=("processed_chunk","sum"),
            duplicates=("dup_chunk","sum"),
            nondup=("nondup_chunk","sum"),
            ranked=("ranked_nondup","sum"),
            labeled=("labeled_nondup","sum"),
        )
    )

    # include all docs
    DocumentBaseline_numeric = (
        DocumentBaseline[["baseid"]].drop_duplicates()
        .merge(calc, on="baseid", how="left")
        .fillna({"processed":0,"duplicates":0,"nondup":0,"ranked":0,"labeled":0})
    )

    # --- DATA QUALITY / CONSISTENCY CHECKS ---
    m_inconsistent = (
        (DocumentBaseline_numeric.duplicates > DocumentBaseline_numeric.processed) |
        (DocumentBaseline_numeric.ranked > DocumentBaseline_numeric.nondup) |
        (DocumentBaseline_numeric.labeled > DocumentBaseline_numeric.ranked)
    )

    # Reconciled document buckets and chart data

    df = DocumentBaseline_numeric.copy()

    # normalize numeric columns and derive non-duplicate chunk count per doc
    for col in ["processed","duplicates","ranked","labeled"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    df["nondup"] = (df["processed"] - df["duplicates"]).clip(lower=0)

    # core doc-level masks
    m_ingested = pd.Series(True, index=df.index)
    m_accepted = df.processed > 0
    m_rejected = ~m_accepted

    m_all_dups = m_accepted & (df.duplicates == df.processed)
    m_low_ctx  = m_accepted & (df.nondup > 0) & (df.ranked == 0) & (df.labeled == 0)

    # candidate docs that actually have non-duplicate chunks and aren't all-dups or low-context
    m_candidate = m_accepted & (df.nondup > 0) & ~m_all_dups & ~m_low_ctx

    # labeling buckets (mutually exclusive; allow labels with ranked==0 to fall into "partially labeled")
    m_fully   = m_candidate & (df.ranked > 0) & (df.labeled == df.ranked) & (df.labeled > 0)
    m_notlab  = m_candidate & (df.ranked > 0) & (df.labeled == 0)
    m_partial = m_candidate & ~m_fully & ~m_notlab & (df.labeled > 0)  # includes ranked==0,labeled>0 and labeled<ranked

    # counts
    numberofdocumentsIngested     = df.loc[m_ingested, "baseid"].nunique()
    numberofdocumentsProcessed    = df.loc[m_accepted, "baseid"].nunique()
    numberofdocumentsNOTProcessed = df.loc[m_rejected, "baseid"].nunique()

    numberofdocumentsDuplicates   = df.loc[m_all_dups, "baseid"].nunique()
    numberofdocumentsLowContext   = df.loc[m_low_ctx, "baseid"].nunique()

    # ToBeLabeled = accepted minus (low context + duplicates)
    numberofdocumentsTobeLabeled  = numberofdocumentsProcessed - numberofdocumentsLowContext - numberofdocumentsDuplicates

    numberofdocumentsFullyLabeled     = df.loc[m_fully, "baseid"].nunique()
    numberofdocumentsPartiallyLabeled = df.loc[m_partial, "baseid"].nunique()
    numberofdocumentsNOTLabeled       = df.loc[m_notlab, "baseid"].nunique()

    # sanity checks (reconcilable)
    assert numberofdocumentsIngested - numberofdocumentsNOTProcessed == numberofdocumentsProcessed
    assert numberofdocumentsProcessed - numberofdocumentsLowContext - numberofdocumentsDuplicates == numberofdocumentsTobeLabeled
    assert numberofdocumentsTobeLabeled - numberofdocumentsFullyLabeled - numberofdocumentsPartiallyLabeled - numberofdocumentsNOTLabeled == 0

    # chart payload
    x_axis   = ['Ingested', 'Accepted', 'Rejected', 'To Be Labeled', 'Low Context', 'Duplicates', 'Fully Labeled', 'Partially Labeled', 'Not Labeled']
    Ingested = [numberofdocumentsIngested, 0, 0, 0]
    Accepted = [0, numberofdocumentsProcessed, 0, 0]
    Rejected = [0, numberofdocumentsNOTProcessed, 0, 0]

    LowContext  = [0, 0, numberofdocumentsLowContext, 0]
    Duplicates  = [0, 0, numberofdocumentsDuplicates, 0]
    TobeLabeled = [0, 0, numberofdocumentsTobeLabeled, 0]

    FullyLabeled     = [0, 0, 0, numberofdocumentsFullyLabeled]
    PartiallyLabeled = [0, 0, 0, numberofdocumentsPartiallyLabeled]
    NotLabeled       = [0, 0, 0, numberofdocumentsNOTLabeled]

    data = [x_axis, Ingested, Accepted, Rejected, TobeLabeled, LowContext, Duplicates, FullyLabeled, PartiallyLabeled, NotLabeled]

    return {'tabledata':data,
    'percents_pages':{'anylabeled':int(df.labeled.sum()),
    'totalprepared':int(df.processed.sum())},
    'percents_documents':{'anylabeled':int(numberofdocumentsFullyLabeled+numberofdocumentsPartiallyLabeled),
    'totalprepared':int(numberofdocumentsTobeLabeled)}}

