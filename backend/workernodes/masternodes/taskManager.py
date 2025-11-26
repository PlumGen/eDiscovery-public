from sqlalchemy import Table, Column, text, String, select, inspect, func, update
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone, timedelta
import os
import pandas as pd
import socket
import uuid
import time

from masternodes.trackLabeleledNodes import trackLabeleledNodes
from masternodes.trackLPropNodes import trackLPropNodes
from masternodes.trackLRevPropNodes import trackLRevPropNodes 
from masternodes.trackLDisAmbigNodes import trackLDisAmbigNodes 

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy.exc import OperationalError

machine_name = socket.gethostname()
unique_id = f"{socket.gethostname()}_{uuid.getnode()}"

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
  
table_name__coordination_tasks = os.environ.get("COORDINATIONTASKS")
table_name__coordination_lock = os.environ.get("COORDINATIONLOCK")
lockexpirationsCheck = int(os.environ.get("LOCK_EXPIRATION_MINUTES"))
listofOperations = os.environ.get("LISTOFOPERATIONS")
embedTable = os.environ.get("EMBEDDATATEXTTABLE") 
table_name__propogation_progress  = os.environ.get("PROPOGATIONPROGRESS")
listofOperations = listofOperations.split(',')
table_name_masterLabels    = os.environ.get("MASTERNODELABELS")

sleepTime_env    = int(os.environ.get("SLEEPTIMEUNTILNEXTTASK"))

AdditionalOperations = os.environ.get("ADDITIONALOPERATIONS")
AdditionalOperations = AdditionalOperations.split(',')

AdditionalOperations_initial = os.environ.get("ADDITIONALOPERATIONSINITIAL")
AdditionalOperations_initial = AdditionalOperations_initial.split(',')
progress_table_name = os.environ["DATATEXTTABLESTATUS"]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def renew_lock(db, lock_key: str, acquired_by: str=unique_id) -> bool:
    now = datetime.now(timezone.utc)

    with db.conn_tx() as conn:
        result = conn.execute(
            update(db.tables[table_name__coordination_lock])
            .where(
                db.tables[table_name__coordination_lock].c.lock_key == lock_key,
                db.tables[table_name__coordination_lock].c.acquired_by == acquired_by
            )
            .values(acquired_at=now)
        )
        return result.rowcount == 1  # ✅ True if lock was found and updated

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def acquire_lock(db, lock_key: str, acquired_by: str):
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    expiration_threshold = now - timedelta(minutes=lockexpirationsCheck)

    result=None
    with db.conn_read() as conn:
        # Check if the lock exists and is still valid
        result = conn.execute(
            text(f"""
                SELECT acquired_at, acquired_by FROM {table_name__coordination_lock}
                WHERE lock_key = :lock_key
            """),
            {"lock_key": lock_key}
        ).fetchone()

    with db.conn_tx() as conn:
        if result:
            if result[1]==acquired_by:
                return True
            elif result[0] > expiration_threshold:
                return False  # ⛔ Lock is still valid
            else:
                # 🔄 Expired — remove and try to acquire
                conn.execute(
                    text(f"DELETE FROM {table_name__coordination_lock} WHERE lock_key = :lock_key"),
                    {"lock_key": lock_key}
                )

        # Try acquiring lock
        try:
            conn.execute(
                insert(db.tables[table_name__coordination_lock]).values(
                    lock_key=lock_key,
                    acquired_by=acquired_by,
                    acquired_at=now
                )
            )
            return True  # ✅ Lock acquired
        except Exception:
            return False  # ⛔ Failed again due to race


def markDone(db, task_key: str, model_key: str):
    print('marking Done')
    if model_key=='All':
        markStageCompleted(db)
        
    else:
        listofModelsProcess = [{"task_name":task_key,
                "model_name":model_key,"status":"done"}]
        
        db.insert_into_table(
            table_name=table_name__coordination_tasks,
            rows=listofModelsProcess,
            batch_size=500,
            conflict_key = ["task_name", "model_name"],
            autoLoad=False,
            do_update=True
        ) 

    
def initialTablePopulation(db):
    print('Initial Population: {initialTablePopulation(db)  }')
    trackLabeleledNodes(db)
    if 'L1_Propogation' in listofOperations:
        trackLPropNodes(db)
    if 'Reverse_L1_Propogation' in listofOperations:    
        trackLRevPropNodes(db)
    if 'DisAmbiguation' in listofOperations:        
        trackLDisAmbigNodes(db)
    TrackingTablePopulate(db)
    return  getlabelledNodesCount(db)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def getlabelledNodesCount(db):
    query = f"""
    SELECT COUNT(*) FROM (
        SELECT 1
        FROM (
            SELECT row_hash,
                   ROW_NUMBER() OVER (PARTITION BY row_hash ORDER BY confidence DESC, id) AS rank
            FROM {table_name_masterLabels}
        ) ranked
        WHERE rank = 1
    ) counted
    """
    with db.conn_read() as conn:
        result = conn.execute(text(query)).scalar()
    return result

def getlabelledNodesCountMaster(db):
    numRowsLabelled_Initial_master = getlabelledNodesCount(db)
    if numRowsLabelled_Initial_master==0:
        
        numRowsLabelled_Initial_master = initialTablePopulation(db)   

    return numRowsLabelled_Initial_master      

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))
def getListofTasks(db):
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
    if status_df.shape[0]<1:
        #initialize tasks 
        TrackingTablePopulate(db)
        with db.conn_read() as conn:
            status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
    return status_df   
   
def checkforcurrentAdditOps(db):
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__propogation_progress}"), conn)
        
    additional_flat_list = None    
    if status_df[~status_df.additionalops.isna()].shape[0]>0:
        additional_flat_list = list(set([item for sublist in status_df.additionalops.dropna() for item in sublist]))

    return additional_flat_list
    
def initProgressTable(db):
    print('Initializing Propogation Process Tables')
    currentlyPopulated   = getlabelledNodesCountMaster(db)
    statusofTasks        = getListofTasks(db)
    additional_flat_list = checkforcurrentAdditOps(db)
    
    if additional_flat_list is None:
        additional_flat_list = AdditionalOperations_initial
        
    listofModelsProcess = [{'method':list(set(statusofTasks.task_name))[0], 'numrowsbefore':currentlyPopulated, 'numrowsafter':None, 'additionalops':additional_flat_list}]
    
    db.insert_into_table(
        table_name=table_name__propogation_progress,
        conflict_key = ["method"],
        rows=listofModelsProcess,
        batch_size=500,
        autoLoad=False,        
        do_update=True
    ) 

    return True

def getAdditionalOperations(db):

    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__propogation_progress}"), conn)

    flat_list = list(set().union(*status_df.additionalops.dropna()))


    for items in AdditionalOperations:
        if items not in flat_list:
            flat_list.append(items)
            break

    if len(set(AdditionalOperations) - set(set().union(*status_df.additionalops.dropna())))>0:
        # Convert Python list to PostgreSQL array format
        array_literal = "{" + ",".join(f'"{item}"' for item in flat_list) + "}"

        with db.conn_tx() as conn:
            conn.execute(text(f"""
                UPDATE {table_name__propogation_progress}
                SET additionalops = :array_val
            """), {"array_val": array_literal})
    
    else:
        ##all operations exhausted
        #inject completion flag and exit 
        
        value_to_insert = "DISAMBIGUATIONCOMPLETE"       
        stmt = insert(db.tables[progress_table_name]).values(status_text=value_to_insert).on_conflict_do_nothing()

        with db.conn_tx() as conn:
            conn.execute(stmt)        
    

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))    
def updateProgressTable(db):
    currentlyPopulated = getlabelledNodesCountMaster(db)
    statusofTasks      = getListofTasks(db)
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__propogation_progress}"), conn)
        
    propogationExhausted=False

    indexforthisRound = status_df[status_df.method==list(set(statusofTasks.task_name))[0]].index
    status_df.loc[indexforthisRound, 'numrowsafter'] = currentlyPopulated
    if all([i in status_df.method.to_list() for i in listofOperations]):
        if all(status_df.numrowsbefore==status_df.numrowsafter):
            propogationExhausted=True
        
    status_df = status_df[status_df.method==list(set(statusofTasks.task_name))[0]]
    status_dict = status_df.to_dict('records')
    status_dict[0]['numrowsafter']=currentlyPopulated
    
    print(status_dict)
    db.insert_into_table(
        table_name=table_name__propogation_progress,
        rows=status_dict,
        batch_size=500,
        conflict_key = ["method"],
        autoLoad=False,
        do_update=True
    ) 
    
    if propogationExhausted:getAdditionalOperations(db)
    
    return status_dict[0], propogationExhausted

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))    
def TrackingTablePopulate(db, nextOperationPassed=None):

    with db.conn_tx() as conn:
        conn.execute(text(f"DELETE FROM {table_name__coordination_tasks}"))
    with db.conn_tx() as conn:
        conn.execute(text(f"DELETE FROM {table_name__coordination_lock}"))

    if nextOperationPassed is None:
        nextOperationPassed = listofOperations[0]
        
    with db.conn_read() as conn:
        result = conn.execute(text(f"SELECT DISTINCT(model_name) FROM {embedTable}"))
        modelstoProcess = result.fetchall()

    listofModelsProcess = []
    for models in modelstoProcess:
        listofModelsProcess.append({"task_name":nextOperationPassed,
        "model_name":models[0],"status":"pending"})


    db.insert_into_table(
        table_name=table_name__coordination_tasks,
        rows=listofModelsProcess,
        batch_size=500,
        conflict_key = ["task_name", "model_name"],
        autoLoad=False,        
        do_update=False
    ) 
    
    initProgressTable(db)
    
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(OperationalError))    
def GetNextTask(db):
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
        
    query = text(f"SELECT COUNT(*) FROM {table_name_masterLabels}")
    with db.conn_read() as conn:
        count = conn.execute(query).scalar()

    if count < 1:
        print("Table is empty")
            
    if status_df.shape[0]<1 or count < 1:
        TrackingTablePopulate(db)
        with db.conn_read() as conn:
            status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
        
        
    print("🔍 Full Task Table:")
    print(status_df)

    nextTask = {}

    pending_df = status_df[status_df.status == 'pending']
    print(f"🕒 Pending tasks: {pending_df.shape[0]}")

    if not pending_df.empty:
        for _, row in pending_df.iterrows():
            lock_key = f"{row.task_name}:{row.model_name}"
            print(f"🔐 Attempting to acquire lock for: {lock_key}")
            if acquire_lock(db, lock_key, unique_id):
                print(f"✅ Lock acquired for: {lock_key}")
                nextTask = {'Process': row.task_name, 'model': row.model_name}
                return nextTask
            else:
                print(f"⛔ Lock held for: {lock_key}")

    elif (status_df.status == 'done').all():
        print("📦 All tasks are marked done, trying aggregation locks...")
        for task in status_df['task_name'].unique():
            lock_key = f"{task}:All"
            print(f"🔐 Attempting to acquire lock for: {lock_key}")
            if acquire_lock(db, lock_key, unique_id):
                print(f"✅ Lock acquired for aggregation: {lock_key}")
                nextTask = {'Process': task, 'model': 'All'}
                return nextTask
            else:
                print(f"⛔ Aggregation lock held for: {lock_key}")

    if not nextTask:
        print("⚠️ No task selected. All locks may be held by others.")
        print('⏳ Sleeping 10 minutes — waiting for eligible task')
        time.sleep(sleepTime_env)
        return GetNextTask(db)
    
    return nextTask    

### if all, then determine whether to proceed
def markStageCompleted(db):
    statusofProgress, propogationExhausted = updateProgressTable(db)
    if statusofProgress['numrowsafter']>statusofProgress['numrowsbefore']:
        nextStage = statusofProgress['method']
        
    else:
        # proceeed to next phase
        try:
            nextStage = listofOperations[listofOperations.index(statusofProgress['method'])+1]
        except:nextStage = listofOperations[0]
    # 1) if progress in current method, then redo, and replace before with after
#    else:
        ##go to additional operations
#        print('Need to Proceed to Additional Operations')
#        nextStage = 'Additional Operations'
    ## any stage that has progress, then redo that stage
    ## else, proceed to next stage
    ## if none of the stages progress, then propogation has been exhausted
       ## reduce confidence threshold so that progression can continue down to a certain limit
       ## if propogation still stalls, then ask for additional manual labelings  
    
    TrackingTablePopulate(db, nextOperationPassed=nextStage)
    