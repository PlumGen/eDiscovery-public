
from sqlalchemy import Table, Column, MetaData, String, select

from sqlalchemy import text, MetaData, Table, inspect
from sqlalchemy.dialects.postgresql import insert
from io import BytesIO
import pandas as pd
import py7zr
import tempfile

import os
import hashlib
from collections import defaultdict
import zipfile, tarfile, gzip, bz2
from sqlalchemy import types as T
### Cloud Specific blob reads
from .readbuckets import azurebucket 

def create_empty_table_from_df(conn, table_name, df: pd.DataFrame, replace=True):
    if replace:
        conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))

    def map_dtype(dtype):
        if pd.api.types.is_integer_dtype(dtype):
            return T.BigInteger()        # handles pandas nullable Int64 too
        if pd.api.types.is_float_dtype(dtype):
            return T.Float()
        if pd.api.types.is_bool_dtype(dtype):
            return T.Boolean()
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return T.DateTime(timezone=False)
        if pd.api.types.is_datetime64tz_dtype(dtype):
            return T.DateTime(timezone=True)
        if pd.api.types.is_timedelta64_dtype(dtype):
            return T.Interval()
        if pd.api.types.is_categorical_dtype(dtype):
            return T.Text()
        if pd.api.types.is_string_dtype(dtype) or dtype == object:
            return T.Text()
        return T.Text()  # fallback

    md = MetaData()
    cols = [Column(str(c), map_dtype(df.dtypes[i])) for i, c in enumerate(df.columns)]
    Table(table_name, md, *cols, schema=None)
    md.create_all(bind=conn)
    
def try_read_csv(file):
    try:
        return pd.read_csv(file, encoding='utf-8', on_bad_lines='skip')
    except Exception:
        try:
            return pd.read_excel(BytesIO(file.read()))
        except Exception as e:
            print(f"Failed to read file: {e}")
            return None


def row_hash(row):
    row_str = "|".join([str(x) for x in row])
    return hashlib.md5(row_str.encode()).hexdigest()


if os.environ.get('RUNENV')!='CUBE':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
BUCKETNAME = os.environ.get("BUCKETNAME")
table_name = os.environ.get("RAWDATATEXTTABLE")
progress_table_name = os.environ.get("DATATEXTTABLESTATUS")
        


def add_missing_columns(df, table_name, db, add_id=True):
    inspector = inspect(db.engine)
    existing_cols = set(col['name'] for col in inspector.get_columns(table_name))
    df_cols = set(df.columns)
    missing = df_cols - existing_cols

    print(f"Existing columns: {existing_cols}")
    print(f"Missing columns: {missing}")

    for col in missing:
        dtype = df[col].dtype
        sql_type = "TEXT"
        if dtype.kind in "iuf": sql_type = "DOUBLE PRECISION"
        elif dtype.kind == "b": sql_type = "BOOLEAN"

        with db.conn_tx() as conn:
            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col} {sql_type}"))

    if add_id and "id" not in existing_cols:
        with db.conn_tx() as conn:
            conn.execute(text(f"""
                ALTER TABLE {table_name}
                ADD COLUMN id BIGSERIAL PRIMARY KEY
            """))
        print(f"✅ Added auto-incrementing 'id' column.")

    print(f"✅ Added columns: {missing}")


def main_ingestdata(db, bucketnamegiven=None):
    engine = db.get_engine()     
    inspector = inspect(engine)
    # Check and create the table if it doesn't exist

    if bucketnamegiven is None:
        bucketnamegiven = BUCKETNAME
    
    countRows = 0


    for blob_name, blob_bytes in azurebucket.yield_blob_bytes(container_name=bucketnamegiven):
        if len(blob_bytes)<1: continue
        grouped_dataframes = defaultdict(list)
        print(f"Processing file: {blob_name}")
        extracted_files = {}

        if blob_name.endswith(".zip"):
            with zipfile.ZipFile(BytesIO(blob_bytes)) as z:
                for file_name in z.namelist():
                    if file_name.endswith(".csv"):
                        with z.open(file_name) as f:
                            df = try_read_csv(f)
                            if df is not None:
                                key = tuple(df.columns)
                                grouped_dataframes[key].append(df)

        elif blob_name.endswith((".tar.gz", ".tgz", ".tar")):
            with tarfile.open(fileobj=BytesIO(blob_bytes), mode="r:*") as tar:
                for member in tar.getmembers():
                    if member.name.endswith(".csv"):
                        f = tar.extractfile(member)
                        if f:
                            df = try_read_csv(f)
                            if df is not None:
                                key = tuple(df.columns)
                                grouped_dataframes[key].append(df)

        elif blob_name.endswith(".gz"):
            with gzip.open(BytesIO(blob_bytes), mode='rt') as f:
                df = try_read_csv(f)
                if df is not None:
                    key = tuple(df.columns)
                    grouped_dataframes[key].append(df)

        elif blob_name.endswith(".bz2"):
            with bz2.open(BytesIO(blob_bytes), mode='rt') as f:
                df = try_read_csv(f)
                if df is not None:
                    key = tuple(df.columns)
                    grouped_dataframes[key].append(df)


        elif blob_name.endswith(".7z"):
            with tempfile.TemporaryDirectory() as tmpdir:
                with py7zr.SevenZipFile(BytesIO(blob_bytes), mode='r') as archive:
                    archive.extractall(path=tmpdir)
                
                for root, _, files in os.walk(tmpdir):
                    for name in files:
                        if name.endswith(".csv"):
                            full_path = os.path.join(root, name)
                            with open(full_path, "rb") as f:
                                df = try_read_csv(f)
                                if df is not None:
                                    key = tuple(df.columns)
                                    grouped_dataframes[key].append(df)



        # Concatenate grouped dataframes
        all_dfs = []
        for schema, dfs in grouped_dataframes.items():
            if len(dfs) > 1:
                print(f"Combining {len(dfs)} files with schema: {schema}")
            all_dfs.append(pd.concat(dfs, ignore_index=True))

        df = pd.concat(all_dfs, ignore_index=True)
        countRows += len(df)
        print(f"Total rows combined: {countRows}")           

        # Clean and deduplicate
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.fillna("NULL")
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
        df['row_hash'] = df.apply(row_hash, axis=1)
        df = df.drop_duplicates(subset=['row_hash'])


        # If first time, create table and index
        # if not inspector.has_table(table_name):
#            print(f"Table {table_name} does not exist — creating.")
        with db.conn_tx() as conn:
            create_empty_table_from_df(conn, table_name, df)
        add_missing_columns(df, table_name, db)

        with db.conn_tx() as conn:
            conn.execute(text(f"""
                CREATE UNIQUE INDEX IF NOT EXISTS uniq_rowhash_idx ON {table_name} (row_hash);
            """))

    # Ensure table + metadata loaded

        rows_to_insert = df.to_dict(orient='records')
        db.insert_into_table(
            table_name=table_name,
            rows=rows_to_insert, 
            conflict_key="row_hash",
            do_update=False,
            autoLoad=True,
            batch_size=500
        )

        print(f"Injected raw data DataFrame into '{table_name}'.")


    print(f"Total raw CSV rows: {countRows}")

    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    column_names = [col["name"] for col in columns]

    print('column names')
    print(column_names)


    dataingest_complete=False
    with db.conn_read() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = result.scalar()  # Gets the first column of the first row
        print(f"Number of rows in {table_name}: {row_count}")
        dataingest_complete = row_count == countRows
    print(f"number of lines in raw bucket: {countRows}")


    if dataingest_complete:
        # Load the table
        db.create_schema_and_indexes()
        
        # Insert a new unique status value
        value_to_insert = "DATAINGESTCOMPLETE"
        stmt = insert(db.tables[progress_table_name]).values(status_text=value_to_insert).on_conflict_do_nothing()

        with db.conn_tx() as conn:
            conn.execute(stmt)
                    
    return True
