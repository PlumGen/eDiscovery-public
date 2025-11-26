from sqlalchemy import Table, Column, text, String, select, inspect, func, update
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone, timedelta
import os
import pandas as pd
import socket
import uuid
import time
import sys

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from sqlalchemy.exc import OperationalError

machine_name = socket.gethostname()
unique_id = f"{socket.gethostname()}_{uuid.getnode()}"

if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
table_name__coordination_tasks = os.environ.get("EMBEDCOORDINATIONTASKS")
table_name__coordination_lock = os.environ.get("EMBEDCOORDINATIONLOCK")
table_name__propogation_progress  = os.environ.get("EMBEDPROGRESS")

lockexpirationsCheck = int(os.environ.get("LOCK_EXPIRATION_MINUTES"))
tokenTable = os.environ.get("TOKENIZEDATATEXTTABLE") 
sleepTime_env    = int(os.environ.get("SLEEPTIMEUNTILNEXTTASK"))
listofOperations = ['embed']


@retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry=retry_if_exception_type(OperationalError))
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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry=retry_if_exception_type(OperationalError))
def acquire_lock(db, lock_key: str, acquired_by: str):
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    expiration_threshold = now - timedelta(minutes=lockexpirationsCheck)

    with db.conn_read() as conn:
        # Check if the lock exists and is still valid
        result = conn.execute(
            text(f"""
                SELECT acquired_at FROM {table_name__coordination_lock}
                WHERE lock_key = :lock_key
            """),
            {"lock_key": lock_key}
        ).fetchone()
        
    with db.conn_tx() as conn:
        if result:
            if result[0] > expiration_threshold:
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

    
    

@retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry=retry_if_exception_type(OperationalError))
def getListofTasks(db):
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
    if status_df.shape[0]<1:
        #initialize tasks 
        TrackingTablePopulate(db)
        with db.conn_read() as conn:
            status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
    return status_df   
   
def initProgressTable(db):
    print('Initializing Propogation Process Tables')

    statusofTasks      = getListofTasks(db)
    listofModelsProcess = [{'method':list(set(statusofTasks.task_name))[0], 'numrowsbefore':0, 'numrowsafter':0}]
    db.insert_into_table(
        table_name=table_name__propogation_progress,
        conflict_key = ["method"],
        rows=listofModelsProcess,
        batch_size=500,
        autoLoad=False,        
        do_update=True
    ) 

    return True

@retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry=retry_if_exception_type(OperationalError))    
def updateProgressTable(db):
    
    statusofTasks      = getListofTasks(db)
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__propogation_progress}"), conn)
    status_df = status_df[status_df.method==list(set(statusofTasks.task_name))[0]]
    status_dict = status_df.to_dict('records')
    status_dict[0]['numrowsafter']=0

    db.insert_into_table(
        table_name=table_name__propogation_progress,
        rows=status_dict,
        batch_size=500,
        conflict_key = ["method"],
        autoLoad=False,
        do_update=True
    ) 
    
    return status_dict[0]

@retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry=retry_if_exception_type(OperationalError))    
def TrackingTablePopulate(db, nextOperationPassed=None):

    with db.conn_read() as conn:
        conn.execute(text(f"DELETE FROM {table_name__coordination_tasks}"))
    with db.conn_read() as conn:
        conn.execute(text(f"DELETE FROM {table_name__coordination_lock}"))

    if nextOperationPassed is None:
        nextOperationPassed = listofOperations[0]
        
    with db.conn_read() as conn:
        result = conn.execute(text(f"SELECT DISTINCT(model_name) FROM {tokenTable}"))
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
    
@retry(stop=stop_after_attempt(3), wait=wait_fixed(30), retry=retry_if_exception_type(OperationalError))    
def GetNextTask(db):
    with db.conn_read() as conn:
        status_df = pd.read_sql(text(f"SELECT * FROM {table_name__coordination_tasks}"), conn)
                   
    if status_df.shape[0]<1:
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
        sys.exit(1)
        
        time.sleep(sleepTime_env)
        
        return GetNextTask(db)
    
    return nextTask    

### if all, then determine whether to proceed
def markStageCompleted(db):
    statusofProgress = updateProgressTable(db)
    if statusofProgress['numrowsafter']>statusofProgress['numrowsbefore']:
        nextStage = statusofProgress['method']
         
    else:
        # proceeed to next phase
        try:
            nextStage = listofOperations[listofOperations.index(statusofProgress['method'])+1]
        except:nextStage = listofOperations[0]
    # 1) if progress in current method, then redo, and replace before with after

    ## any stage that has progress, then redo that stage
    ## else, proceed to next stage
    ## if none of the stages progress, then propogation has been exhausted
       ## reduce confidence threshold so that progression can continue down to a certain limit
       ## if propogation still stalls, then ask for additional manual labelings  
    
    #TrackingTablePopulate(db, nextOperationPassed=nextStage)
    