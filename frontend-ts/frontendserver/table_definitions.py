
from sqlalchemy import Table, Column, MetaData, String, UniqueConstraint, BigInteger, ForeignKey, inspect, Text, Float, Integer, Index, text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import os
from sqlalchemy import CheckConstraint
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql import func

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
progress_table_name  = os.environ.get("DATATEXTTABLESTATUS")
table_name_cleantext = os.environ.get("CLEANEDDATATEXTTABLE")
table_name_tokenize  = os.environ.get("TOKENIZEDATATEXTTABLE")
table_name_embed     = os.environ.get("EMBEDDATATEXTTABLE")

table_name_simpairs         = os.environ.get("SIMPAIRSDATATEXTTABLE")
table_name_deduplicates     = os.environ.get("MARKEDDUPLICATESTEXTTABLE")
table_name_ranking          = os.environ.get("RANKINGDATATEXTTABLE")
table_name_clustering       = os.environ.get("CLUSTERINGDATATEXTTABLE")
table_name_labelcandidates       = os.environ.get("LABELCANDIDATESTABLE")
table_name_labelcandidates_validation = os.environ.get("LABELCANDIDATESVALIDATIONTABLE")
table_name_prepropogationtable = os.environ.get("PREPROPOGATEDLABELS")
table_name_reverseprepropogationtable = os.environ.get("REVERSEPREPROPOGATEDLABELS")
table_name_disambiguationtable = os.environ.get("DISAMBIGUATIONLABELS")

table_name__master_node_label_candidates = os.environ.get("MASTERNODELABELS")

table_name__coordination_tasks = os.environ.get("COORDINATIONTASKS")
table_name__coordination_lock = os.environ.get("COORDINATIONLOCK")
table_name__propogation_progress  = os.environ.get("PROPOGATIONPROGRESS")

table_name_embed_coordination_tasks = os.environ.get("EMBEDCOORDINATIONTASKS")
table_name_embed_coordination_lock = os.environ.get("EMBEDCOORDINATIONLOCK")
table_name__emebd_progress  = os.environ.get("EMBEDPROGRESS")

rawdatatext_tablename = os.environ.get("RAWDATATEXTTABLE")
rawdocument_tablename = os.environ.get("RAWDATADOCUMENTTABLE")

issuedefinition_tablename = os.environ.get("LABELISSUEDEFINITIONS")

def define_tables(metadata):
        
    rawdatatext = Table(rawdatatext_tablename, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key                            
        Column("row_hash", String, unique=True),   
        Column("docid", String, unique=True),         
        Column("filename", String, unique=False, nullable=True),
        Column("blob_name", String, unique=False, nullable=True), 
        Column("Body", String, unique=False),         

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
              
        extend_existing=True)  # allows merging with real later

        
    progress_table = Table(
        progress_table_name, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key    
        Column("status_text", String, nullable=False, unique=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        # You can add more columns here if needed
    )

    cleandatatext = Table(
        table_name_cleantext, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key       
        Column("docid", Text, ForeignKey("rawdatatext.row_hash"), nullable=False),
        Column("chunkid", BigInteger, nullable=False),
        Column("chunk_text", Text, nullable=True),
        Column("clean_text", Text, nullable=True),
        Column("num_sentences", BigInteger, nullable=False),
        Column("row_hash", Text, unique=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
    )

    tokenizeddata = Table(
        table_name_tokenize, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key         
        Column("clean_text", Text, nullable=True),
        Column("docid", Text, nullable=False),
        Column("chunkid", BigInteger, nullable=False),
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("row_hash_model", Text, nullable=False),
        Column("num_sentences", BigInteger, nullable=True),
        Column("tokenized", Text, nullable=True),
        Column("wordcount", BigInteger, nullable=True),
        Column("alphanumeric", Float, nullable=True),  # DOUBLE PRECISION → Float
        Column("token_count", BigInteger, nullable=True),
        Column("model_name", Text, nullable=False),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hash_model", name="uniq_row_hash_tokenized")
    )

    embeddata = Table( 
        table_name_embed, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key       
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("row_hash_model", String, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),    
        Column("num_sentences", Integer, nullable=True),
        Column("wordcount", Integer, nullable=True),
        Column("alphanumeric", Float, nullable=True),
        Column("token_count", Integer, nullable=True),
        Column("model_name", String, nullable=False),
        Column("embed", JSONB, nullable=True),  # Use JSONB if using PostgreSQL dialect

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hash_model", name="uniq_row_hash_embed")
    )

    simpairdata = Table(
        table_name_simpairs, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key         
        Column("source_idx", Integer, nullable=False),
        Column("target_idx", BigInteger, nullable=False),
        Column("similarity", Float, nullable=False),
        Column("source_row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),
        Column("target_row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),
        Column("source_row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("target_row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),        
        Column("source_num_sentence", BigInteger, nullable=True),
        Column("target_num_sentence", BigInteger, nullable=True),
        Column("model_name", Text, nullable=True),
        Column("row_hash_tablespec", Text, nullable=False),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hash_tablespec", name="uniq_row_hash_simpairs")
    )

    markedduplicates = Table(
        table_name_deduplicates, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key          
        Column("role", Text, nullable=True),
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("row_hash_master", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),        
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),
        Column("row_hash_model_master", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
    )

    rankingtable = Table(
        table_name_ranking, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),        
        Column("row_hash_model", String, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),
        Column("model_name", String, nullable=False),
        Column("Selection_Rank_Deterministic", Integer, nullable=True),
        Column("Selection_Distance", Float, nullable=True), 

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hash_model", name="uniq_row_hash_rank") 
    )

    clusteringtable = Table(
        table_name_clustering, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key     
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False, unique=True),
        Column("model_name", String, nullable=True),    
        Column("spectral_max", Text, nullable=True),
        Column("spectral_balanced", Text, nullable=True),
        Column("louvain", Text, nullable=True),
        Column("leiden", Text, nullable=True),
        Column("hdbscan", Text, nullable=True),
        Column("hdbscan_fix", Text, nullable=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hash_model", name="uniq_row_hash_cluster")  
    )

    labelcandidates = Table(
        table_name_labelcandidates, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key       
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False, unique=True),                 
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False, unique=True),
        Column("model_name", Text, nullable=True),
        Column("user_label", ARRAY(Text), nullable=True),
        Column("user_label_code", Text, nullable=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                              
        UniqueConstraint("row_hash", name="uniq_row_hash_label")  
    )

    labelcandidatesvalidation = Table(
        table_name_labelcandidates_validation, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key        
        Column("similarity", Float, nullable=True),
        Column("source_row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("target_row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),        
        Column("source_row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),
        Column("target_row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),
        Column("source_user_label", ARRAY(Text), nullable=True),
        Column("target_user_label", ARRAY(Text), nullable=True),
        Column("matching_labels", Boolean, nullable=True),
        Column("row_hashtablespec", Text, nullable=True, unique=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hashtablespec", name="uniq_row_hash_cluster_valid")  
    )

    prepropogationtable = Table(
        table_name_prepropogationtable, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key        
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False, unique=False),
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False, unique=True),        
        Column("user_label_standard", Text, nullable=False),
        Column("computehardware", Text, nullable=False),            
        Column("confidence", Float, nullable=False),
        Column("timestamp", Float, nullable=False),        
        Column("category_reassign_l1_source", ARRAY(Text), nullable=False),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
    )    

    reverseprepropogationtable = Table(
        table_name_reverseprepropogationtable, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key        
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False, unique=False),
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False, unique=True),        
        Column("user_label_standard", Text, nullable=False),
        Column("computehardware", Text, nullable=False),            
        Column("confidence", Float, nullable=False),
        Column("timestamp", Float, nullable=False),        
        Column("category_reassign_l1_source", ARRAY(Text), nullable=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
    )   

    master_node_label_candidates = Table(
        table_name__master_node_label_candidates, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # surrogate key
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False, unique=True),  # can be row_hash or internal uid
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False),  # can be row_hash or internal uid
        Column("label", Text, nullable=False),
        Column("user_reassign", Text, nullable=True),
        Column("computehardware", Text, nullable=False),
        Column("confidence", Float, nullable=False),
        Column("method", Text, nullable=False),  # e.g., 'manual', 'L1', 'L2', 'hybrid'
        Column("model_votes", Integer, nullable=True),  # optional, null if not relevant
        Column("timestamp", Float, nullable=True),  # optional for tracking when label was added
        Column("label_distribution", ARRAY(Float), nullable=True),  # optional: soft scores

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        UniqueConstraint("row_hash", name="uq_row_model_method")
        )

    disambiguationtable = Table(
        table_name_disambiguationtable, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key         
        Column("row_hash", Text, ForeignKey("cleandatatext.row_hash"), nullable=False),
        Column("row_hash_model", Text, ForeignKey("tokenizeddata.row_hash_model"), nullable=False, unique=True),  # can be row_hash or internal uid        
        Column("user_label_standard", Text, nullable=False),
        Column("computehardware", Text, nullable=False),
        Column("numberofrounds", Text, nullable=False),                
        Column("confidence", Float, nullable=False),      
        Column("timestamp", Float, nullable=True),  # optional for tracking when label was added          
        Column("user_label_standard_source", ARRAY(Text), nullable=True),
        Column("category_reassign_l1_source", ARRAY(Text), nullable=True),       

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                       
        CheckConstraint(
            "(cardinality(category_reassign_l1_source) > 0 OR cardinality(user_label_standard_source) > 0)",
            name="at_least_one_array_nonempty"
        ),
        UniqueConstraint("row_hash_model", name="uq_row_hash_model")  # ✅ Explicit constraint

    )
    
    coordination_tasks = Table(
        table_name__coordination_tasks, metadata,
        Column("task_name", Text, primary_key=True),            # e.g. 'l1_prop', 'disambiguate'
        Column("model_name", Text, primary_key=True),           # e.g. 'modelA', 'modelB', or 'all' for aggregation
        Column("status", Text, nullable=False),                 # e.g. 'pending', 'running', 'done'
        Column(
            "acquired_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('UTC', now())")
        )
        )

    propogation_progress = Table(
        table_name__propogation_progress, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key              
        Column("method", Text, nullable=False, unique=True),            # e.g. 'l1_prop', 'disambiguate'
        Column("numrowsbefore", BigInteger, nullable=False),           # e.g. 'modelA', 'modelB', or 'all' for aggregation
        Column("numrowsafter", BigInteger, nullable=True),                 # e.g. 'pending', 'running', 'done'
        Column("additionalops", ARRAY(Text), nullable=True, server_default=text("ARRAY['IncludeDuplicates']::text[]")),
        Column(
            "acquired_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('UTC', now())")
        )
        )
    
    coordination_lock = Table(
        table_name__coordination_lock, metadata,
        Column("lock_key", Text, primary_key=True),             # e.g. 'l1_prop:modelA'
        Column("acquired_by", Text, nullable=False),            # machine or process name
        Column(
            "acquired_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('UTC', now())")
        )
        )
       
    embed_coordination_tasks = Table(
        table_name_embed_coordination_tasks, metadata,
        Column("task_name", Text, primary_key=True),            # e.g. 'l1_prop', 'disambiguate'
        Column("model_name", Text, primary_key=True),           # e.g. 'modelA', 'modelB', or 'all' for aggregation
        Column("status", Text, nullable=False),                 # e.g. 'pending', 'running', 'done'
        Column(
            "acquired_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('UTC', now())")
        )
        )

    embed_progress = Table(
        table_name__emebd_progress, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key              
        Column("method", Text, nullable=False, unique=True),            # e.g. 'l1_prop', 'disambiguate'
        Column("numrowsbefore", BigInteger, nullable=False),           # e.g. 'modelA', 'modelB', or 'all' for aggregation
        Column("numrowsafter", BigInteger, nullable=True),                 # e.g. 'pending', 'running', 'done'
        Column(
            "acquired_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('UTC', now())")
        )
        )

    embed_coordination_lock = Table(
        table_name_embed_coordination_lock, metadata,
        Column("lock_key", Text, primary_key=True),             # e.g. 'l1_prop:modelA'
        Column("acquired_by", Text, nullable=False),            # machine or process name
        Column(
            "acquired_at",
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("TIMEZONE('UTC', now())")
        )
        )
    
    issuedefinition = Table(issuedefinition_tablename, metadata,
        Column("id", BigInteger, primary_key=True, autoincrement=True),  # 👈 new surrogate key                            
        Column("issuename", String, unique=True),
        Column("issuedefinition", String, unique=True),

        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
                      
        extend_existing=True)  # allows merging with real later
        

    return {
    progress_table_name:progress_table,
    rawdatatext_tablename:rawdatatext, 
    table_name_cleantext:cleandatatext, 
    table_name_tokenize:tokenizeddata, 
    table_name_embed:embeddata,
    table_name_simpairs:simpairdata, 
    table_name_deduplicates:markedduplicates, 
    table_name_ranking:rankingtable, 
    table_name_clustering:clusteringtable,
    table_name_labelcandidates:labelcandidates, 
    table_name_labelcandidates_validation:labelcandidatesvalidation,
    table_name_prepropogationtable:prepropogationtable,
    table_name_disambiguationtable:disambiguationtable,
    table_name__master_node_label_candidates:master_node_label_candidates,
    table_name_reverseprepropogationtable:reverseprepropogationtable,
    table_name__coordination_tasks:coordination_tasks,
    table_name__coordination_lock:coordination_lock,
    table_name__propogation_progress:propogation_progress,
    table_name_embed_coordination_tasks:embed_coordination_tasks,
    table_name__emebd_progress:embed_progress,
    table_name_embed_coordination_lock:embed_coordination_lock,
    issuedefinition_tablename:issuedefinition, 
    
    }