import prepprogresstabulations.getTableofDocumentsProgress as getTableofDocumentsProgress
import prepprogresstabulations.getReviewedStats as getReviewedStats
import prepprogresstabulations.getdocumentsLabeledProgress as getdocumentsLabeledProgress
import os
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func

progress_tabulations_name = os.environ.get("PRETABULATIONSPROGRESS")

tableNamingMaps = {'getdocumentsLabeledProgress':'progresstype_overall',
                   'getReviewedStats':'progresstype_reviewedstats',
                   'getTableofDocumentsProgress':'progresstype_listofpropogateddocuments'}

def runTableInsertions(tablemapping, dictvalue, selected_db):
    value_to_insert = {'tablemapping': tablemapping, 'dictvalue': dictvalue}
    stmt = insert(selected_db.tables[progress_tabulations_name]).values(value_to_insert).on_conflict_do_update(
        index_elements=["tablemapping"],   # column(s) defining the conflict
        set_={                             # what to update when conflict happens
            "dictvalue": value_to_insert["dictvalue"],
            "updated_at": func.now()
        }
    )

    with selected_db.conn_tx() as conn:
        conn.execute(stmt)
    
def populatecurrentprogress(db):    

    getTableofDocumentsProgress_results= getTableofDocumentsProgress.getTableofDocumentsProgress(db)
    runTableInsertions(tableNamingMaps['getTableofDocumentsProgress'], getTableofDocumentsProgress_results, db)

    getReviewedStats_results = getReviewedStats.getReviewedStats(db)
    runTableInsertions(tableNamingMaps['getReviewedStats'], getReviewedStats_results, db)


    getdocumentsLabeledProgress_results= getdocumentsLabeledProgress.getdocumentsLabeledProgress(db)
    runTableInsertions(tableNamingMaps['getdocumentsLabeledProgress'], getdocumentsLabeledProgress_results, db)

    return True