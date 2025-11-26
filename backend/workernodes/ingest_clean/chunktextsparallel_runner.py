from multiprocessing import Pool, cpu_count
import pandas as pd
from .chunktextsparallel import chunk_doc_worker, init_worker


def chunk_documents_parallel(rows, chunk_size=512, overlap=100, processes=None, regex_list=None, baselineModels = None, columnaNames=None):
    if processes is None:
        processes = min(cpu_count(), 8)
    if baselineModels is None:
        initargs=("BAAI/bge-large-en", "en_core_web_md")
    else:initargs=baselineModels
    
    if columnaNames is None:
        columnaNames = {'docid':'docid',
                        'Body':'Body'}  
    

    with Pool(
        processes=processes,
        initializer=init_worker,
        initargs=initargs
    ) as pool:
        all_results = pool.starmap(chunk_doc_worker, [(row, chunk_size, overlap, regex_list, columnaNames) for row in rows])

    flat_records = [item for sublist in all_results for item in sublist]
    return pd.DataFrame(flat_records)
