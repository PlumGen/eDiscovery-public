# database_manager.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import Table, Column, MetaData, String, UniqueConstraint, BigInteger, ForeignKey, inspect, Text, Float, Integer, Index, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from table_definitions import define_tables
from sqlalchemy.sql.expression import text

from sqlalchemy.exc import OperationalError
import time
    
import os
import urllib.parse 
from urllib.parse import quote_plus

import pandas as pd

class DatabaseManager:
    def __init__(self, db_name=None):
        self.engine = None
        self.metadata = MetaData()
        self.db_name = db_name
        self.tables = define_tables(self.metadata)        
        self._init_engine()
        

    def _init_engine(self):
        if os.environ.get('RUNENV') != 'CUBE':
            from dotenv import load_dotenv
            load_dotenv(override=True)

        db_username = os.getenv('DB_USERNAME', 'postgres')   #for debug project only
        db_password = os.getenv('DB_PASSWORD', 'N(?~TTn--vtCkhK0')   #for debug project only
        db_ip = os.getenv('HOST', '/cloudsql/ediscovery-452217:us-east4:ediscoverydemo')   #for debug project only
        db_port = os.getenv('DBPORT', '5432')   #for debug project only
        if self.db_name is None:
            db_name = os.getenv('DB_NAME', 'postgres')   #for debug project only
        else:db_name = self.db_name
        local = os.getenv('RUNENV', 'LOCAL')   #for debug project only

        db_password_enc = urllib.parse.quote(db_password)
        db_password_quote = quote_plus(db_password)

        if local == 'LOCAL': 
            db_host = '127.0.0.1'    #for debug project only
        elif local == 'DOCKER':
            db_host = 'host.docker.internal'    #for debug project only
        elif local == 'AZURE':
            db_host = "mypgserver45678.postgres.database.azure.com"    #for debug project only
        elif local == 'CUBE':
            db_host = os.getenv('DB_HOST') 

        else:
            db_host = db_ip

        additionaltext = '/postgres?host='
        engine_url_list = [
            f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}",
            f"postgresql+psycopg2://{db_username}:{db_password_enc}@{additionaltext}{db_host}",
            f"postgresql+psycopg2://{db_username}:{db_password_quote}@{additionaltext}{db_host}"
        ]

        for engine_url in engine_url_list:
            try:
                print(f"Trying connection string: {engine_url}")
                engine = create_engine(engine_url,     pool_pre_ping=True,       # checks connection before using it
                    pool_recycle=1800,        # recycles connections older than 30 minutes
                    pool_size=10,             # number of connections in pool
                    max_overflow=20,          # how many more can be created beyond pool_size
                    echo=False,               # set to True if debugging SQL
                )
                
                self._test_connection(engine)
                self.engine = engine
                print("✅ Database engine initialized.")
                return
            except Exception as e:
                print(f"⚠️ Failed with: {e}")
                continue

        raise RuntimeError("❌ Could not establish a connection to the database.")

    def _test_connection(self, engine):
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1

    def createTriggerfunctions(self):
        table_name_labelcandidates       = os.environ.get("LABELCANDIDATESTABLE")
        table_name_labelcandidates_validation = os.environ.get("LABELCANDIDATESVALIDATIONTABLE")
        
        table_name_labelcandidates_validation = self.tables[table_name_labelcandidates_validation]#Table(table_name_labelcandidates_validation, self.metadata, autoload_with=self.engine)
        table_name_labelcandidates            = self.tables[table_name_labelcandidates]#Table(table_name_labelcandidates, self.metadata, autoload_with=self.engine)
                        
        trigger_function_sql = f"""
                    CREATE OR REPLACE FUNCTION update_user_labels()
                    RETURNS TRIGGER AS $$
                    BEGIN
                    -- propagate labels
                    UPDATE {table_name_labelcandidates_validation}
                    SET source_user_label = NEW.user_label
                    WHERE source_row_hash = NEW.row_hash;

                    UPDATE {table_name_labelcandidates_validation}
                    SET target_user_label = NEW.user_label
                    WHERE target_row_hash = NEW.row_hash;

                    -- True when source ≠ target (order-insensitive, NULL-safe)
                    UPDATE {table_name_labelcandidates_validation}
                    SET matching_labels = (
                        COALESCE((SELECT array_agg(s ORDER BY s) FROM unnest(source_user_label) s), ARRAY[]::text[])
                        IS DISTINCT FROM
                        COALESCE((SELECT array_agg(t ORDER BY t) FROM unnest(target_user_label) t), ARRAY[]::text[])
                    )
                    WHERE source_row_hash = NEW.row_hash
                        OR target_row_hash = NEW.row_hash;

                    RETURN NEW;
                    END;
                    $$ LANGUAGE plpgsql;
        """


        trigger_sql = f"""
        DROP TRIGGER IF EXISTS trg_update_user_labels ON {table_name_labelcandidates};

        CREATE TRIGGER trg_update_user_labels
        AFTER UPDATE OF user_label ON {table_name_labelcandidates}
        FOR EACH ROW
        WHEN (OLD.user_label IS DISTINCT FROM NEW.user_label)
        EXECUTE FUNCTION update_user_labels();
        """

        createindex = f"""CREATE INDEX ON {table_name_labelcandidates_validation} (source_row_hash);
        CREATE INDEX ON {table_name_labelcandidates_validation} (target_row_hash);
        """


        with self.engine.begin() as conn:
            conn.execute(text(trigger_function_sql))
            conn.execute(text(trigger_sql))
            conn.execute(text(createindex))
            print("✅ Trigger and function installed for propagating user_label updates.")
          

    def create_schema_and_indexes(self):
        # Bind metadata to the engine

        # Define indexes 
        index_list = [
        
        Index("idx_tokenizeddata_row_hash_model", self.tables['tokenizeddata'].c.row_hash_model), 
        Index("idx_embeddata_model_name", self.tables['embeddata'].c.model_name),
        Index("idx_embeddata_row_hash_model", self.tables['embeddata'].c.row_hash_model),         
        Index("idx_simpairdata_source_target", self.tables['simpairdata'].c.source_row_hash, self.tables['simpairdata'].c.target_row_hash),
        
        Index("idx_simpairdata_similarity", self.tables['simpairdata'].c.similarity), 
        Index("idx_simpairdata_source_sentencelen", self.tables['simpairdata'].c.source_num_sentence), 
        Index("idx_simpairdata_target_sentencelen", self.tables['simpairdata'].c.target_num_sentence), 
        
        Index("idx_markedduplicates_master", self.tables['markedduplicates'].c.row_hash_master),
        Index("idx_markedduplicates_", self.tables['markedduplicates'].c.row_hash),
        
        Index("idx_rankingtable_model_name", self.tables['rankingtable'].c.row_hash_model),
        Index("idx_clusteringtable_model", self.tables['clusteringtable'].c.row_hash_model),
        Index("idx_labelcandidates_userlabel", self.tables['labelcandidates'].c.row_hash_model),
        Index("idx_labelcandidates_userlabel_userlabel", self.tables['labelcandidates'].c.user_label),        
        Index("idx_labelcandidatesvalidation_similarity", self.tables['labelcandidatesvalidation'].c.similarity),
        Index("idx_labelcandidatesvalidation_source", self.tables['labelcandidatesvalidation'].c.source_row_hash),
        Index("idx_labelcandidatesvalidation_target", self.tables['labelcandidatesvalidation'].c.target_row_hash),
        Index("idx_prepropogation_row_hash", self.tables['prepropogatedlabelstable'].c.row_hash),  
        Index("idx_prepropogation_row_hash_model", self.tables['prepropogatedlabelstable'].c.row_hash_model),  
        
        Index("idx_dismbiguationtable_row_hash", self.tables['dismbiguationtable'].c.row_hash),  
        Index("idx_dismbiguationtable_row_hash_model", self.tables['dismbiguationtable'].c.row_hash_model),  
                                
        Index("idx_masterlabelstable_row_hash", self.tables['masterlabelstable'].c.row_hash),  
        Index("idx_masterlabelstable_row_hash_model", self.tables['masterlabelstable'].c.row_hash_model),  
        ]
        
        
        self.metadata.create_all(
            self.engine, 
            tables=[table for name, table in self.tables.items()]
        )

        # Explicitly create all indexes
        for idx in index_list:
            idx.create(bind=self.engine, checkfirst=True)
        
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()               
        
        print("✅ Tables and indexes created.")

    def get_engine(self):
        return self.engine

    def get_metadata(self):
        return self.metadata


    def insert_into_table(self, table_name, rows, conflict_key=None, do_update=False, batch_size=1000, where_flag=False, autoLoad=True, exclude_columns=None):
        """
        Insert rows into a table with optional conflict handling and batching.

        :param table_name: str, name of the table
        :param rows: list of dicts (e.g., from df.to_dict(orient='records'))
        :param conflict_key: str, column name with unique constraint to resolve conflicts
        :param do_update: bool, if True do update on conflict; otherwise do nothing
        :param batch_size: int, number of rows per batch
        """
        if isinstance(conflict_key, str):
            conflict_key = [conflict_key]
             
        if autoLoad:
            table = Table(table_name, MetaData(), autoload_with=self.engine)
        else:
            table = Table(table_name, self.metadata)
            
        if exclude_columns is None:
            exclude_columns = ["created_at", "updated_at"]

        # Sanitize rows
        cleaned_rows = []
        for row in rows:
            cleaned = {k: v for k, v in row.items() if k not in exclude_columns}
            cleaned_rows.append(cleaned)
        

        for i in range(0, len(cleaned_rows), batch_size):
            batch = cleaned_rows[i:i + batch_size]
            stmt = pg_insert(table).values(batch)
            if conflict_key:
                if do_update:
                    update_set = {
                                    c.name: stmt.excluded[c.name]
                                    for c in table.c
                                    if c.name not in conflict_key and not c.primary_key
                                }

                    if where_flag:
                        stmt = stmt.on_conflict_do_update(
                            index_elements=conflict_key,
                            set_=update_set,
                            where=stmt.excluded.confidence > table.c.confidence
                        )
                    else:
                        stmt = stmt.on_conflict_do_update(
                            index_elements=conflict_key,
                            set_=update_set
                        )
                else:
                    stmt = stmt.on_conflict_do_nothing(index_elements=conflict_key)
            self.execute_statement_resilient(stmt)

    def execute_statement_resilient(self, stmt, retries=3):
        for attempt in range(retries):
            try:
                with self.engine.begin() as conn:
                    conn.execute(stmt)
                    return True
            except OperationalError as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
                raise
        
    def resilient_read_query_keyset(
        self,
        base_query,
        key_column='id',
        start_after=0,
        chunksize=1000,
        retries=3,
        delay=5,
        params=None,
        in_clause_param_key='hashes',
        in_clause_chunk_size=1000
    ):
        if isinstance(base_query, str):
            base_query = text(base_query)

        params = dict(params or {})
        last_seen = start_after

        is_expanding = hasattr(base_query, 'bindparams') and any(
            getattr(p, 'expanding', False) and p.key == in_clause_param_key
            for p in base_query._bindparams.values()
        )

        if is_expanding:
            # 🔁 Split values into chunks and run without pagination
            all_values = params[in_clause_param_key]
            for i in range(0, len(all_values), in_clause_chunk_size):
                chunk_values = all_values[i:i + in_clause_chunk_size]
                chunk_params = dict(params)
                chunk_params[in_clause_param_key] = tuple(chunk_values)

                for attempt in range(retries):
                    try:
                        with self.engine.connect() as conn:
                            df = pd.read_sql_query(base_query, conn, params=chunk_params)
                            df = df.loc[:, ~df.columns.duplicated()]
                        yield df
                        break
                    except OperationalError:
                        if attempt < retries - 1:
                            time.sleep(delay)
                        else:
                            raise
            return

        # 🔁 Keyset pagination for normal queries
        base_query_str = str(base_query).strip().rstrip(';')

        while True:
            if 'where' in base_query_str.lower():
                pagination_clause = f" AND {key_column} > :last_seen"
            else:
                pagination_clause = f" WHERE {key_column} > :last_seen"

            paginated_query = text(f"""
                {base_query_str}
                {pagination_clause}
                ORDER BY {key_column}
                LIMIT {chunksize}
            """)

            query_params = dict(params)
            query_params["last_seen"] = last_seen

            for attempt in range(retries):
                try:
                    with self.engine.connect() as conn:
                        chunk = pd.read_sql_query(paginated_query, conn, params=query_params)
                        chunk = chunk.loc[:, ~chunk.columns.duplicated()]
                    break
                except OperationalError:
                    if attempt < retries - 1:
                        time.sleep(delay)
                    else:
                        raise

            if chunk.empty:
                break

            yield chunk

            if key_column not in chunk.columns:
                break
            last_seen = int(chunk[key_column].iloc[-1])