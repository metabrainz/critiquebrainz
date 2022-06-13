from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

DEFAULT_CACHE_EXPIRATION = 12 * 60 * 60  # seconds (12 hours)
bb_engine = None


def init_db_engine(connect_str):
    global bb_engine
    bb_engine = create_engine(connect_str, poolclass=NullPool)


def run_sql_script(sql_file_path):
    with open(sql_file_path) as sql:
        connection = bb_engine.connect()
        connection.execute(sql.read())
        connection.close()
