from database_manager import DatabaseManager 
import controlcontainers.controllingcontainer_switch as controllingcontainer_switch 
from sqlalchemy import create_engine
from sqlalchemy import text

def selectDB(projectselected=None, threadsafe=False, selectionmap={}):
    if projectselected is None:
        return False

    db_name = selectionmap[projectselected]['db_name']
    return DatabaseManager(db_name=db_name)


def runControlSwitch(company, selectionmap, userinjesttype=''):

    selected_db = selectDB(projectselected=company, threadsafe=True, selectionmap=selectionmap)
    # (Optional) verify connection is writable
    with selected_db.conn_read() as conn:
        readonly = conn.execute(text("SHOW transaction_read_only;")).scalar()
        if readonly == 'on':
            raise RuntimeError("Database is read-only — check endpoint or permissions")

    controllingcontainer_switch.runworkerjobs(
        db=selected_db,
        bucketname=selectionmap[company]['bucket'],
        userinjesttype=userinjesttype
    )
    print(f"runworkerjobs started for {company}")
    selected_db.engine.dispose()
    
    return True
