import logging
import os
from datetime import timedelta
from typing import Optional

from cachelib.file import FileSystemCache
from celery.schedules import crontab
from cachelib.redis import RedisCache

logger = logging.getLogger()


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)

#---------------------------------------------------------
# Flask App Builder configuration
#---------------------------------------------------------
# App secret key
## Create a secret key to replace the superset default key:
#from cryptography import fernet
#secret = fernet.Fernet.generate_key()
secret = get_env_variable("FERNET_KEY")
# App secret key changed from default
SECRET_KEY = secret


DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT")
DATABASE_DB = get_env_variable("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

# Set up a Result Backend with s3
# pass an instance of a derivative of S3Cache to the RESULTS_BACKEND configuration key
#from s3cache.s3cache import S3Cache
S3_CACHE_BUCKET = 'foo-data-applications'
S3_CACHE_KEY_PREFIX = 'applications/apache-superset/apache-superset-cache'
#RESULTS_BACKEND = S3Cache(S3_CACHE_BUCKET, S3_CACHE_KEY_PREFIX)
RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

# The S3 bucket where you want to store your external hive tables created
# from CSV files. For example, 'companyname-superset'
CSV_TO_HIVE_UPLOAD_S3_BUCKET = S3_CACHE_BUCKET
# The directory within the bucket specified above that will
# contain all the external tables
CSV_TO_HIVE_UPLOAD_DIRECTORY = "applications/apache-superset/apache-superset-cache/EXTERNAL_HIVE_TABLES/"


REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = get_env_variable("REDIS_RESULTS_DB", "1")
REDIS_FILTER_DB = get_env_variable("REDIS_FILTER_DB", "2")
REDIS_CHARTS_DB = get_env_variable("REDIS_CHARTS_DB", "3")

# Cache for filters state
FILTER_STATE_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400, # 1 day
    "CACHE_KEY_PREFIX": "superset_filter_",
    "CACHE_THRESHOLD": 0,
    "REFRESH_TIMEOUT_ON_RETRIEVAL": True,
    "CACHE_REDIS_URL": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_FILTER_DB}"
}

# Cache for chart form data
EXPLORE_FORM_DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    'CACHE_DEFAULT_TIMEOUT': 86400, # 1 day
    'CACHE_KEY_PREFIX': 'superset_chart_',
    "CACHE_THRESHOLD": 0,
    "REFRESH_TIMEOUT_ON_RETRIEVAL": True,
    "CACHE_REDIS_URL": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CHARTS_DB}"

}

class CeleryConfig(object):
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    CELERY_IMPORTS = ("superset.sql_lab", "superset.tasks")
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    CELERYD_LOG_LEVEL = "DEBUG"
    CELERYD_PREFETCH_MULTIPLIER = 1
    CELERY_ACKS_LATE = False
    CELERYBEAT_SCHEDULE = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig
RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST, port=REDIS_PORT, key_prefix='superset_results')

FEATURE_FLAGS = {"ALERT_REPORTS": False}
#ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
#WEBDRIVER_BASEURL = "http://superset:8088/"
# The base URL for the email report hyperlinks.
#WEBDRIVER_BASEURL_USER_FRIENDLY = WEBDRIVER_BASEURL

SQLLAB_CTAS_NO_LIMIT = True

## Add User Self-registration ability
#AUTH_USER_REGISTRATION = True
#AUTH_USER_REGISTRATION_ROLE = "custom_role"

# https://medium.com/@nileshxbhosale/apache-superset-a-cost-effective-alternative-to-quick-sight-for-data-lake-668868fe51c7
# Configure emailing protocol
ENABLE_SCHEDULED_EMAIL_REPORTS = False
EMAIL_NOTIFICATIONS = False

## smtp server configuration
#SMTP_HOST = "email-smtp.ap-south-1.amazonaws.com"
#SMTP_STARTTLS = False
#SMTP_SSL = True
#SMTP_USER = ""
#SMTP_PORT = 465
#SMTP_PASSWORD = ""
#SMTP_MAIL_FROM = "no-reply@company.com"

# Email reports - minimum time resolution (in minutes) for the crontab
#EMAIL_REPORTS_CRON_RESOLUTION = 15
# Email report configuration
# From address in emails

EMAIL_REPORT_FROM_ADDRESS = None
# Send bcc of all reports to this address. Set to None to disable.
# This is useful for maintaining an audit trail of all email deliveries.
EMAIL_REPORT_BCC_ADDRESS = None

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
#try:
    #import superset_config_docker
    #from superset_config_docker import *  # noqa

    #logger.info(
        #f"Loaded your Docker configuration at " f"[{superset_config_docker.__file__}]"
    #)
#except ImportError:
    #logger.info("Using default Docker config...")
