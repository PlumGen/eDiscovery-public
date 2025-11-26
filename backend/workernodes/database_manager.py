# database_manager.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import Table, Column, MetaData, String, UniqueConstraint, BigInteger, ForeignKey, inspect, Text, Float, Integer, Index, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from table_definitions import define_tables
from sqlalchemy.sql.expression import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.sql.ddl import CreateTable, CreateIndex
from contextlib import contextmanager
from sqlalchemy.exc import OperationalError, InternalError
from sqlalchemy.engine import URL

import socket, random
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

    # ---------- helpers ----------
    def _dns_resolves(self, host: str, attempts=5, delay=1.0):
        """Resolve host with small retry + jitter to mask transient NXDOMAIN."""
        last_err = None
        for i in range(attempts):
            try:
                socket.getaddrinfo(host, None)  # supports A/AAAA
                return True
            except socket.gaierror as e:
                last_err = e
                time.sleep(delay * (1.5 ** i) + random.uniform(0, 0.2))
        raise last_err

    def _extract_host(self, url: str) -> str:
        """Works for both normal DSN and '/postgres?host=...' style."""
        try:
            u = make_url(url)
            if u.host:
                return u.host
        except Exception:
            pass
        # fallback parse for '?host=' pattern
        if "host=" in url:
            return url.split("host=")[-1].split("&")[0].split("?")[0]
        return url

    def _test_connection(self, engine):
        # do not start a transaction just to test the link
        with engine.connect() as conn:
            conn = conn.execution_options(isolation_level="AUTOCOMMIT")
            r = conn.execute(text("SELECT 1"))
            # scalar_one() is stricter; scalar() is ok too
            assert r.scalar_one() == 1

    

    @contextmanager
    def conn_read(self):
        # true autocommit; no implicit begin()
        conn = self.engine.execution_options(isolation_level="AUTOCOMMIT").connect()
        try:
            # pool hygiene in case a dirty conn slipped through
            try:
                if conn.in_transaction():
                    conn.rollback()
            except Exception:
                pass
            yield conn
        finally:
            conn.close()

    @contextmanager
    def conn_tx(self):
        # explicit transaction for writes
        conn = self.engine.connect()
        trans = None
        try:
            try:
                if conn.in_transaction():
                    conn.rollback()
            except Exception:
                pass
            trans = conn.begin()
            yield conn
            trans.commit()
        except Exception:
            if trans is not None and trans.is_active:
                trans.rollback()
            raise
        finally:
            conn.close()


    # ---------- for GCS only ----------
    def linksforcloudsql(self, db_username, db_password, db_port, db_name, db_host):
        additionaltext = '/postgres?host='
        db_password_enc = urllib.parse.quote(db_password)
        
        db_url = URL.create(
            "postgresql+pg8000",
            username=db_username,
            password=db_password,
            database=db_name,
            query={
                # this is the *only* thing pg8000 needs for the Unix socket
                "unix_sock": f"{db_host}/.s.PGSQL.5432",
            },
        )
        
        return [db_url]
    
    # ---------- init ----------
    def _init_engine(self):
        if os.environ.get('RUNENV') != 'CUBE':
            from dotenv import load_dotenv
            load_dotenv(override=True)

        db_username = os.getenv('DB_USERNAME', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'N(?~TTn--vtCkhK0')
        db_ip       = os.getenv('HOST', '/cloudsql/genial-reporter-399805:us-central1:ediscovery-test5')
        db_port     = os.getenv('DBPORT', '5432')
        db_name     = self.db_name or os.getenv('DB_NAME', 'postgres')
        local       = os.getenv('RUNENV', 'LOCAL')

        db_password_enc   = urllib.parse.quote(db_password)
        db_password_quote = quote_plus(db_password)

        if local == 'LOCAL':
            db_host = '127.0.0.1'
        elif local == 'DOCKER':
            db_host = 'host.docker.internal'
        elif local == 'AZURE':
            db_host = "mypgserver45678.postgres.database.azure.com"
        elif local == 'CUBE':
            db_host = os.getenv('DB_HOST')
        else:
            db_host = db_ip

        # DSNs to try (keep your existing fallbacks)
        engine_url_list = [
            f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}",
            f"postgresql+psycopg2://{db_username}:{db_password_enc}@/postgres?host={db_host}",
            f"postgresql+psycopg2://{db_username}:{db_password_quote}@/postgres?host={db_host}",
        ]
        
        
        connect_args = {
            
        }

                    
        if db_host == db_ip:
            engine_url_list=self.linksforcloudsql(db_username, db_password, db_port, db_name, db_host)
        else:
            # libpq keepalives: ONLY for psycopg2
            connect_args.update(
                {
                    "options": "-c statement_timeout=30000",
                    "keepalives": 1,
                    "keepalives_idle": 30,
                    "keepalives_interval": 10,
                    "keepalives_count": 3,
                }
            )
                            
        MAX_RETRIES = 6
        BASE_BACKOFF = 3  # seconds

        last_error = None
        for engine_url in engine_url_list:
            if isinstance(engine_url, str):
                host = self._extract_host(engine_url)
            else:host=None
            
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    print(f"Trying connection string: {engine_url} (attempt {attempt}/{MAX_RETRIES})")

                    # DNS warm-up with retry (handles intermittent NXDOMAIN)
                    if host:
                        print('Running DNS resolution check for host:', host)
                        self._dns_resolves(host)
                        print('DNS resolution successful for host:', host)
                    print('Creating database engine...')
                    
                    eng = create_engine(
                        engine_url,
                        pool_pre_ping=True,   # validate before checkout
                        pool_recycle=300,     # retire idle conns quickly
                        pool_size=10,
                        max_overflow=20,
                        pool_timeout=30,
                        connect_args=connect_args,
                        echo=False,
                        pool_reset_on_return="rollback"
                    )

                    # test immediately; attach auto-dispose on failure
                    self._test_connection(eng)

                    @event.listens_for(eng, "engine_connect")
                    def _ensure_connect(connection, branch):
                        if branch:
                            return
                        try:
                            connection.scalar(text("SELECT 1"))
                        except Exception:
                            connection.engine.dispose()
                            raise

                    @event.listens_for(eng, "checkout")
                    def _rollback_on_checkout(dbapi_conn, conn_record, conn_proxy):
                        try:
                            dbapi_conn.rollback()
                        except Exception:
                            pass
    
                    self.engine = eng
                    print("✅ Database engine initialized.")
                    return
                except (OperationalError, SQLAlchemyError, Exception) as e:
                    last_error = e
                    sleep_time = BASE_BACKOFF * (2 ** (attempt - 1)) + random.uniform(0, 0.5)
                    if attempt < MAX_RETRIES:
                        print(f"⚠️ Failed with: {e}\nRetrying in {sleep_time:.1f}s...")
                        time.sleep(sleep_time)
                    else:
                        print("❌ Max retries reached for this connection string. Trying next...")
                        break

        raise RuntimeError(f"❌ Could not establish a connection to the database. Last error: {last_error}")

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


        with self.conn_read() as conn:
            conn.execute(text(trigger_function_sql))
            conn.execute(text(trigger_sql))
            conn.execute(text(createindex))
            print("✅ Trigger and function installed for propagating user_label updates.")
          

    def create_schema_and_indexes(self):
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

        # brand-new engine to avoid contaminated pool
        engine = create_engine(self.engine.url, pool_pre_ping=True, future=True)
        raw = engine.raw_connection()
        try:
            # psycopg2: true autocommit at driver level (no SQLA transaction ever starts)
            try:
                raw.autocommit = True
            except Exception:
                # psycopg3 fallback
                raw.isolation_level = None

            cur = raw.cursor()

            # create tables (IF NOT EXISTS to be idempotent)
            for tbl in self.metadata.sorted_tables:
                ddl = CreateTable(tbl, if_not_exists=True).compile(dialect=engine.dialect)
                cur.execute(str(ddl))

            # create indexes (idempotent)
            for idx in index_list:
                ddl = CreateIndex(idx, if_not_exists=True).compile(dialect=engine.dialect)
                cur.execute(str(ddl))

            cur.close()
            try:
                raw.commit()
            except Exception:
                pass

            insp = inspect(engine)
            print("✅ Tables and indexes created:", insp.get_table_names())

        finally:
            try:
                raw.close()
            except Exception:
                pass
            engine.dispose()

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
                with self.conn_tx() as conn:
                    conn.execute(stmt)
                    return True

            except (OperationalError, InternalError) as e:
                # Detect "read-only transaction" or other transactional corruption
                if "read-only transaction" in str(e) or "in failed sql transaction" in str(e):
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    self.engine.dispose()  # drop bad connections from pool

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
                        with self.conn_read() as conn:
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
                    with self.conn_read() as conn:
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