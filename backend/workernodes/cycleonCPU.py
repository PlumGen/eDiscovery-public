# ❗ Must be the very first code to run
import os
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.utils.deprecation") 

def set_omp_threads(n=1):
    if "OMP_NUM_THREADS" not in os.environ:
        os.environ["OMP_NUM_THREADS"] = str(n)
        print(f"✅ Set OMP_NUM_THREADS={n}")


set_omp_threads()


# ❗ Top-level, no imports before this
import multiprocessing as mp
import os
import sys

if os.name == 'posix':
    if mp.get_start_method(allow_none=True) != 'spawn':
        mp.set_start_method("spawn", force=True)

# ✅ Now import everything else
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")


# Delayed imports (none of these can be top-level if they transitively use multiprocessing)
from sqlalchemy import inspect
from database_manager import DatabaseManager
from sqlalchemy import Table, Column, text, String, select, func
from propogate.cyclePropogations import runNextPropogation

try:import RunCheck
except:import licensecheck.RunCheck

from loadDLLs import add_dll_directories_from_site_packages
# Use it before importing any .pyd/.dll-based modules
dll_dirs = add_dll_directories_from_site_packages()
#print("🔗 DLL directories added:", dll_dirs) 

def process_entrypoint(db):

    db.create_schema_and_indexes()
    engine = db.get_engine()
    inspector = inspect(engine)
    print(inspector.get_table_names())

    with db.conn_read() as conn:
        propogated = conn.execute(
            select(db.tables[progress_table_name].c.status_text).where(db.tables[progress_table_name].c.status_text == "DISAMBIGUATIONCOMPLETE")
        ).first()
        
        
        
    if propogated:
        print("DISAMBIGUATIONCOMPLETE already exists in progress table.")  
        sys.exit(1)
    else:
        finalNodesLabeled = runNextPropogation(db, RunCheck)

if __name__ == "__main__":
    process_entrypoint()
