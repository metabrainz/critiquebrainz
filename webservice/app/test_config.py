import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import config
from sqlalchemy.engine.url import URL

# by default we assume there exists a database with '_test' suffix
# meant for testing purposes
db_config = config.DATABASE
db_config['database'] += '_test'
db_uri = URL(**db_config)
