from sqlalchemy import Table, Column, text, String, select, inspect
import os
from embedding_models import embedding_models
import torch
import RunCheck

from database_manager import DatabaseManager 

from loadDLLs import add_dll_directories_from_site_packages
# Use it before importing any .pyd/.dll-based modules
dll_dirs = add_dll_directories_from_site_packages()
#print("🔗 DLL directories added:", dll_dirs) 

def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

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

def main_prep_switch(db_name=None):
    
    if db_name is None:
        db = DatabaseManager()
    else:db = DatabaseManager(db_name=db_name)
    
    engine = db.get_engine() 
    

    inspector = inspect(engine)
    # Check and create the table if it doesn't exist
    gpu_available = get_device()
    result=None 
    if inspector.has_table(table_name):
        db.create_schema_and_indexes()

        with db.conn_read() as conn:
            result = conn.execute(
                select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "DATAINGESTCOMPLETE")
            ).first()
    if result and inspector.has_table(table_name):
        print('Master Prep: Data Ingest Complete:')
    else:
        from ingest_clean import main_ingestdata
        main_ingestdata.main_ingestdata(db)

    # Check if TEXTCLEAN is complete
    with db.conn_read() as conn:
        result = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "TEXTCLEANCOMPLETE")
        ).first()

    if result and inspector.has_table(table_name_cleantext): 
        print('Master Prep: Text Clean Complete:')
    else:        
        from ingest_clean import main_cleantext
        main_cleantext.main_cleantext(db)

    # Check if TOKENIZE is complete
    with db.conn_read() as conn:
        result = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "TOKENIZECOMPLETE:ALL")
        ).first()
    if result and inspector.has_table(table_name_tokenize):
        print('Master Prep: Tokenization Complete:')
    else:                       
        from tokenizerlocal import main_tokenizetext
        main_tokenizetext.main_tokenizetext(db, embedding_models)

    # Check if EMBED is complete
    with db.conn_read() as conn:
        result = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "EMBEDCOMPLETE:ALL")
        ).first()
    print(f'runembedoncpu: {runembedoncpu}')
    
    if result and inspector.has_table(table_name_embed):
        print('Master Prep: Embedding Complete:') 
    else:
        
        if runembedoncpu=='True' or gpu_available.type=='cuda':
            print('Loading embed module')
            from embedizelocal import main_embed
            main_embed.main_embed(db, gpu_available) 
    
       # Check if SIMPAIRS are complete
    with db.conn_read() as conn:
        result = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "SIMPAIRSCOMPLETE")
        ).first()
    
    if result and inspector.has_table(table_name_simpairs):
        print('Master Prep: SimPairs Complete:')
    else:
        # Delete downstream artifacts    
        
        from deduplicate import main_simpairs
        main_simpairs.main_simpairs(db)     
                
       # Check if Deduplicates are complete

    with db.conn_read() as conn:
        result = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "DUPLICATESMARKEDCOMPLETE")
        ).first()

    with db.conn_read() as conn:
            duplicatedefinition = conn.execute( 
                select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text.like("%DUPLICATEDEFINITION%"))
            ).first()
        
    if result and inspector.has_table(table_name_deduplicates):
        print('Master Prep: Deduplicates Complete:')
    elif duplicatedefinition:
        # Delete downstream artifacts
                         
        from deduplicate import main_markedduplicates
        main_markedduplicates.main_markedduplicates(db)  

    # check if ranking has been executed
    with db.conn_read() as conn:
        rankingdone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "RANKINGCOMPLETE")
        ).first() 

    with db.conn_read() as conn:
        duplicatesMarked = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "DUPLICATESMARKEDCOMPLETE")
        ).first() 
        
    if rankingdone and inspector.has_table(table_name_ranking):
        print('Master Prep: Ranking Complete:')
        
    elif duplicatesMarked and inspector.has_table(table_name_deduplicates) and (runembedoncpu=='True' or gpu_available.type=='cuda'):
            from rank_cluster import main_runranking
            main_runranking.main_runranking(db, RunCheck)
        
    ## check if clustering is complete
    with db.conn_read() as conn:
        embeddone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "EMBEDCOMPLETE:ALL")
        ).first()      

    with db.conn_read() as conn:
        clusterdone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "CLUSTERCOMPLETE:ALL")
        ).first() 
                   
    if clusterdone and inspector.has_table(table_name_clustering):
        print('Master Prep: Clustering Complete:')
    elif embeddone and inspector.has_table(table_name_embed) and (runembedoncpu=='True' or gpu_available.type=='cuda'):
        from rank_cluster import main_cluster
        main_cluster.main_cluster(db, RunCheck)
        
    ## check if label candidates are complete
    with db.conn_read() as conn:
        embeddone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "EMBEDCOMPLETE:ALL")
        ).first()      

    with db.conn_read() as conn:
        clusterdone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "CLUSTERCOMPLETE:ALL")
        ).first() 

    with db.conn_read() as conn:
        labelcandidatedone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "LABELCANDIDATECOMPLETE")
        ).first() 

    with db.conn_read() as conn:
        rankingdone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "RANKINGCOMPLETE")
        ).first()            
        
    if labelcandidatedone and inspector.has_table(table_name_labelcandidates) and inspector.has_table(table_name_labelcandidates_validation):
        print('Master Prep: Candidate Selection Complete:')
    elif embeddone and inspector.has_table(table_name_embed) and clusterdone and inspector.has_table(table_name_clustering) and rankingdone and inspector.has_table(table_name_ranking):
        from labelcandidates import main_candidatelabels
        main_candidatelabels.main_candidatelabels(db)
                
## if user has labeled nodes
    with db.conn_read() as conn:
        isprepropogated = conn.execute(text(f"SELECT EXISTS (SELECT 1 FROM {table_name_prepropogationtable} LIMIT 1)"))
    isprepropogated = isprepropogated.scalar()
    isprepropogated=True
                              
    with db.conn_read() as conn:
        userdone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "USERLABELEDNODES")
        ).first()   
                     
    with db.conn_read() as conn:
        propogationdone = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "DISAMBIGUATIONCOMPLETE")
        ).first()  
        
    if userdone and isprepropogated and not propogationdone and labelcandidatedone and inspector.has_table(table_name_labelcandidates) and inspector.has_table(table_name_labelcandidates_validation):
        print('Starting DisAmbiguation Cycles:')
        import subprocess
        import sys

        subprocess.Popen([sys.executable, 'cycleonCPU.py'])

                       
    return True

