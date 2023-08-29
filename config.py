import os
from sqlalchemy import create_engine
class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = os.getenv('SECRET_KEY', 'Geoxhr123??')

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://addatsco_geox_user:Addatgeox??@162.214.195.234/addatsco_geox_dashboard'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/geoxhr'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_POOL_TIMEOUT = 60
    SQLALCHEMY_POOL_RECYCLE = 3600

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', 'app/static/assets')




class ProductionConfig(Config):
    DEBUG = False

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

    # PostgreSQL database
    SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
        os.getenv('DB_ENGINE'   , 'mysql'),
        os.getenv('DB_USERNAME' , 'addatsco_geox_user'),
        os.getenv('DB_PASS'     , 'Addatgeox??'),
        os.getenv('DB_HOST'     , 'localhost'),
        os.getenv('DB_PORT'     , 3306),
        os.getenv('DB_NAME'     , 'addatsco_geox_dashboard')
    )
# PostgreSQL database
#     SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
#         os.getenv('DB_ENGINE'   , 'mysql'),
#         os.getenv('DB_USERNAME' , 'root'),
#         os.getenv('DB_PASS'     , ''),
#         os.getenv('DB_HOST'     , 'localhost'),
#         os.getenv('DB_PORT'     , 3306),
#         os.getenv('DB_NAME'     , 'geoxhr')
#     )
class DebugConfig(Config):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
