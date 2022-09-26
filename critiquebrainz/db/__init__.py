from flask_debugtoolbar.panels import sqlalchemy
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
    with open(sql_file_path) as sql, engine.begin() as connection:
        connection.execute(text(sql.read()))


def run_sql_script_without_transaction(sql_file_path):
    with open(sql_file_path) as sql, engine.connect() as connection:
        connection.connection.set_isolation_level(0)
        lines = sql.read().splitlines()
        try:
            for line in lines:
                # TODO: Not a great way of removing comments. The alternative is to catch
                #  the exception sqlalchemy.exc.ProgrammingError "can't execute an empty query"
                if line and not line.startswith("--"):
                    connection.execute(text(line))
        except sqlalchemy.exc.ProgrammingError as e:
            print("Error: {}".format(e))
            return False
        finally:
            connection.connection.set_isolation_level(1)
            connection.close()
        return True
