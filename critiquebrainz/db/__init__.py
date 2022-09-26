from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# This value must be incremented after schema changes on exported tables!
SCHEMA_VERSION = 15

VALID_RATING_VALUES = [None, 1, 2, 3, 4, 5]
REVIEW_RATING_MAX = 5
REVIEW_RATING_MIN = 1
REVIEW_TEXT_MAX_LENGTH = 100000
REVIEW_TEXT_MIN_LENGTH = 25
# Scales for rating conversion
RATING_SCALE_0_100 = {1: 20, 2: 40, 3: 60, 4: 80, 5: 100}
RATING_SCALE_1_5 = {20: 1, 40: 2, 60: 3, 80: 4, 100: 5}

engine = None


def init_db_engine(connect_str):
    global engine
    engine = create_engine(connect_str, poolclass=NullPool)


def run_sql_script(sql_file_path):
    with open(sql_file_path) as sql:
        connection = engine.connect()
        connection.execute(text(sql.read()))
        connection.close()
