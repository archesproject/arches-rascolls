"""
Django settings for arches_rascolls project.
"""

import os
import inspect
import semantic_version
from datetime import datetime, timedelta
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string

try:
    from arches.settings import *
except ImportError:
    pass


def get_env_variable(var_name):
    msg = "Set the %s environment variable"
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = msg % var_name
        raise ImproperlyConfigured(error_msg)


def get_optional_env_variable(var_name, default=None) -> str:
    try:
        return os.environ[var_name]
    except KeyError:
        return default


APP_NAME = "arches_rascolls"

SECRETS_MODE = get_optional_env_variable("ARCHES_SECRETS_MODE", "ENV")

APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

# environment variable names for postgres are built-ins for the pg client, do not modify
DB_NAME = get_optional_env_variable("PGDATABASE", APP_NAME)
DB_USER = get_optional_env_variable("PGUSER", "postgres")
DB_PASSWORD = get_optional_env_variable("PGPASSWORD", "postgis")
DB_HOST = get_optional_env_variable("PGHOST", "localhost")
DB_PORT = get_optional_env_variable("PGPORT", "5432")

ES_USER = get_optional_env_variable("ARCHES_ESUSER", "elastic")
ES_PASSWORD = get_optional_env_variable("ARCHES_ESPASSWORD", "E1asticSearchforArche5")
ES_HOST = get_optional_env_variable("ARCHES_ESHOST", "localhost")
ES_PORT = int(get_optional_env_variable("ARCHES_ESPORT", "9200"))
WEBPACK_DEVELOPMENT_SERVER_PORT = int(
    get_optional_env_variable("ARCHES_WEBPACKDEVELOPMENTSERVERPORT", "8022")
)
ES_PROTOCOL = get_optional_env_variable("ARCHES_ESPROTOCOL", "http")
ES_VALIDATE_CERT = get_optional_env_variable("ARCHES_ESVALIDATE", "True") == "True"
DEBUG = bool(get_optional_env_variable("ARCHES_DJANGO_DEBUG", False))
KIBANA_URL = get_optional_env_variable("ARCHES_KIBANA_URL", "http://localhost:5601/")
KIBANA_CONFIG_BASEPATH = get_optional_env_variable(
    "ARCHES_KIBANACONFIGBASEPATH", "kibana"
)
RESOURCE_IMPORT_LOG = get_optional_env_variable(
    "ARCHES_RESOURCEIMPORTLOG", os.path.join(APP_ROOT, "logs", "resource_import.log")
)
ARCHES_LOG_PATH = get_optional_env_variable(
    "ARCHES_LOGPATH", os.path.join(ROOT_DIR, "arches.log")
)

STORAGE_BACKEND = get_optional_env_variable(
    "ARCHES_STORAGEBACKEND", "django.core.files.storage.FileSystemStorage"
)

if STORAGE_BACKEND == "storages.backends.s3.S3Storage":
    import psutil

    STORAGE_OPTIONS = {
        "bucket_name": get_env_variable("ARCHES_S3BUCKETNAME"),
        "file_overwrite": get_optional_env_variable("ARCHES_S3FILEOVERWRITE", "True")
        == "True",
        "signature_version": get_optional_env_variable(
            "ARCHES_S3SIGNATUREVERSION", "s3v4"
        ),
        "region": get_optional_env_variable("ARCHES_S3REGION", "us-west-1"),
        "max_memory_size": get_optional_env_variable(
            "ARCHES_S3MAXMEMORY", str(psutil.virtual_memory().available * 0.5)
        ),
    }
else:
    STORAGE_OPTIONS = {}

STORAGES = {
    "default": {
        "BACKEND": STORAGE_BACKEND,
        "OPTIONS": STORAGE_OPTIONS,
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"

SECRET_KEY = (
    "debug"
    if DEBUG
    else get_optional_env_variable(
        "ARCHES_SECRET_KEY", "django-insecure-" + get_random_string(50, chars)
    )
)

if SECRETS_MODE == "AWS":
    try:
        import boto3
        import json

        AWS_REGION = get_optional_env_variable("ARCHES_AWS_REGION", "us-west-1")
        ES_SECRET_ID = get_env_variable("ARCHES_ES_SECRET_ID")
        DB_SECRET_ID = get_env_variable("ARCHES_DB_SECRET_ID")
        client = boto3.client("secretsmanager", region_name=AWS_REGION)
        es_secret = json.loads(
            client.get_secret_value(SecretId=ES_SECRET_ID)["SecretString"]
        )
        db_secret = json.loads(
            client.get_secret_value(SecretId=DB_SECRET_ID)["SecretString"]
        )
        ssm_client = boto3.client("ssm", region_name=AWS_REGION)
        DB_NAME = get_optional_env_variable("PGDATABASE", APP_NAME)
        DB_USER = db_secret["username"]
        DB_PASSWORD = db_secret["password"]
        DB_HOST = db_secret["host"]
        DB_PORT = db_secret["port"]
        ES_USER = es_secret["user"]
        ES_PASSWORD = es_secret["password"]
        ES_HOST = es_secret["host"]
        arches_secret_key_id = get_optional_env_variable("ARCHES_SECRET_KEY_ID", None)
        if arches_secret_key_id is not None:
            SECRET_KEY = ssm_client.get_parameter(
                Name=arches_secret_key_id, WithDecryption=True
            )["Parameter"]["Value"]
    except (ModuleNotFoundError, ImportError):
        pass

APP_VERSION = semantic_version.Version(major=0, minor=0, patch=0)
APP_ROOT = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

WEBPACK_LOADER = {
    "DEFAULT": {
        "STATS_FILE": os.path.join(APP_ROOT, "..", "webpack/webpack-stats.json"),
    },
}

DATATYPE_LOCATIONS.append("arches_rascolls.datatypes")
FUNCTION_LOCATIONS.append("arches_rascolls.functions")
ETL_MODULE_LOCATIONS.append("arches_rascolls.etl_modules")
SEARCH_COMPONENT_LOCATIONS.append("arches_rascolls.search_components")

LOCALE_PATHS.insert(0, os.path.join(APP_ROOT, "locale"))

FILE_TYPE_CHECKING = "lenient"
FILE_TYPES = [
    "bmp",
    "gif",
    "jpg",
    "jpeg",
    "json",
    "pdf",
    "png",
    "psd",
    "rtf",
    "tif",
    "tiff",
    "xlsx",
    "csv",
    "zip",
]
FILENAME_GENERATOR = "arches.app.utils.storage_filename_generator.generate_filename"
UPLOADED_FILES_DIR = "uploadedfiles"

ROOT_URLCONF = "arches_rascolls.urls"
ROOT_HOSTCONF = "arches_rascolls.hosts"

ELASTICSEARCH_HOSTS = [{"scheme": ES_PROTOCOL, "host": ES_HOST, "port": ES_PORT}]
# Modify this line as needed for your project to connect to elasticsearch with a password that you generate
ELASTICSEARCH_CONNECTION_OPTIONS = {
    "request_timeout": 30,
    "verify_certs": ES_VALIDATE_CERT,
    "basic_auth": (ES_USER, ES_PASSWORD),
}

DEFAULT_HOST = "arches_rascolls"

# Your Elasticsearch instance needs to be configured with xpack.security.enabled=true to use API keys - update elasticsearch.yml or .env file and restart.

# Set the ELASTIC_PASSWORD environment variable in either the docker-compose.yml or .env file to the password you set for the elastic user,
# otherwise a random password will be generated.

# API keys can be generated via the Elasticsearch API: https://www.elastic.co/guide/en/elasticsearch/reference/current/security-api-create-api-key.html
# Or Kibana: https://www.elastic.co/guide/en/kibana/current/api-keys.html

# a prefix to append to all elasticsearch indexes, note: must be lower case
ELASTICSEARCH_PREFIX = get_optional_env_variable("ARCHES_ES_INDEX_PREFIX", APP_NAME)

REFERENCES_INDEX_NAME = "references"
ELASTICSEARCH_CUSTOM_INDEXES = [
    {
        "module": "arches_controlled_lists.search_indexes.reference_index.ReferenceIndex",
        "name": REFERENCES_INDEX_NAME,
        "should_update_asynchronously": True,
    }
]
TERM_SEARCH_TYPES = [
    {
        "type": "term",
        "label": _("Term Matches"),
        "key": "terms",
        "module": "arches.app.search.search_term.TermSearch",
    },
    {
        "type": "concept",
        "label": _("Concepts"),
        "key": "concepts",
        "module": "arches.app.search.concept_search.ConceptSearch",
    },
    {
        "type": "reference",
        "label": _("References"),
        "key": REFERENCES_INDEX_NAME,
        "module": "arches_controlled_lists.search_indexes.reference_index.ReferenceIndex",
    },
]

ES_MAPPING_MODIFIER_CLASSES = [
    "arches_controlled_lists.search.references_es_mapping_modifier.ReferencesEsMappingModifier"
]

LOAD_DEFAULT_ONTOLOGY = False
LOAD_PACKAGE_ONTOLOGIES = True

PUBLIC_SERVER_ADDRESS = get_optional_env_variable(
    "ARCHES_PUBLIC_SERVER_ADDRESS", "http://localhost:8000/"
)
ARCHES_NAMESPACE_FOR_DATA_EXPORT = get_optional_env_variable(
    "ARCHES_NAMESPACE_FOR_DATA_EXPORT", PUBLIC_SERVER_ADDRESS
)
# [{
#     'module': 'arches_rascolls.search_indexes.sample_index.SampleIndex',
#     'name': 'my_new_custom_index', <-- follow ES index naming rules
#     'should_update_asynchronously': False  <-- denotes if asynchronously updating the index would affect custom functionality within the project.
# }]

KIBANA_URL = "http://localhost:5601/"
KIBANA_CONFIG_BASEPATH = "kibana"  # must match Kibana config.yml setting (server.basePath) but without the leading slash,
# also make sure to set server.rewriteBasePath: true

LOAD_DEFAULT_ONTOLOGY = False
LOAD_PACKAGE_ONTOLOGIES = True

# This is the namespace to use for export of data (for RDF/XML for example)
# It must point to the url where you host your site
# Make sure to use a trailing slash
ARCHES_NAMESPACE_FOR_DATA_EXPORT = "http://localhost:8000/"

DATABASES = {
    "default": {
        "ATOMIC_REQUESTS": False,
        "AUTOCOMMIT": True,
        "CONN_MAX_AGE": 0,
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "OPTIONS": {
            "options": "-c cursor_tuple_fraction=1",
        },
        "HOST": DB_HOST,
        "NAME": DB_NAME,
        "PASSWORD": DB_PASSWORD,
        "PORT": DB_PORT,
        "POSTGIS_TEMPLATE": "template_postgis",
        "TEST": {"CHARSET": None, "COLLATION": None, "MIRROR": None, "NAME": None},
        "TIME_ZONE": None,
        "USER": DB_USER,
    }
}

SEARCH_THUMBNAILS = False

INSTALLED_APPS = (
    "arches_rascolls",  # Ensure the project is listed before any other arches applications
    "webpack_loader",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_hosts",
    "arches_controlled_lists",
    "arches",
    "arches.app.models",
    "arches.management",
    "guardian",
    "django_recaptcha",
    "revproxy",
    "corsheaders",
    "oauth2_provider",
    "django_celery_results",
    "django_migrate_sql",
    # "silk",
    "django.contrib.postgres",
    "arches_modular_reports",
    "rest_framework",
    "arches_querysets",
    "arches_component_lab",
    "arches_search",
    "pgtrigger",
)

# Placing this last ensures any templates provided by Arches Applications
# take precedence over core arches templates in arches/app/templates.
INSTALLED_APPS += (
    "arches.app",
    "django.contrib.admin",
)

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    #'arches.app.utils.middleware.TokenMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "arches.app.utils.middleware.ModifyAuthorizationHeader",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "arches.app.utils.middleware.SetAnonymousUser",
    # "silk.middleware.SilkyMiddleware",
    # "csp.middleware.CSPMiddleware",
]

MIDDLEWARE.insert(  # this must resolve to first MIDDLEWARE entry
    0, "django_hosts.middleware.HostsRequestMiddleware"
)

MIDDLEWARE.append(  # this must resolve last MIDDLEWARE entry
    "django_hosts.middleware.HostsResponseMiddleware"
)

STATICFILES_DIRS = build_staticfiles_dirs(app_root=APP_ROOT)

TEMPLATES = build_templates_config(
    debug=DEBUG,
    app_root=APP_ROOT,
)

ALLOWED_HOSTS = get_optional_env_variable("ARCHES_ALLOWED_HOSTS", "*").split(",")

SYSTEM_SETTINGS_LOCAL_PATH = os.path.join(
    APP_ROOT, "system_settings", "System_Settings.json"
)
WSGI_APPLICATION = "arches_rascolls.wsgi.application"

# URL that handles the media served from MEDIA_ROOT, used for managing stored files.
# It must end in a slash if set to a non-empty value.
MEDIA_URL = "/files/"

# Absolute filesystem path to the directory that will hold user-uploaded files.
MEDIA_ROOT = os.path.join(APP_ROOT)

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/static/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(APP_ROOT, "staticfiles")

# when hosting Arches under a sub path set this value to the sub path eg : "/{sub_path}/"
FORCE_SCRIPT_NAME = None

RESOURCE_IMPORT_LOG = os.path.join(APP_ROOT, "logs", "resource_import.log")
DEFAULT_RESOURCE_IMPORT_USER = {"username": "admin", "userid": 1}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",  # DEBUG, INFO, WARNING, ERROR
            "class": "logging.FileHandler",
            "filename": os.path.join(APP_ROOT, "arches.log"),
            "formatter": "console",
        },
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "arches": {
            "handlers": ["file", "console"],
            "level": "WARNING",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["file", "console"],
            "level": "WARNING",  # or consider ERROR if this is too noisy
            "propagate": True,
        },
        # consider adding your own project here if it logs
    },
}

# Rate limit for authentication views
# See options (including None or python callables):
# https://django-ratelimit.readthedocs.io/en/stable/rates.html#rates-chapter
RATE_LIMIT = "5/m"

# Sets default max upload size to 15MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 15728640

# Unique session cookie ensures that logins are treated separately for each app
SESSION_COOKIE_NAME = "arches_rascolls"

# For more info on configuring your cache: https://docs.djangoproject.com/en/2.2/topics/cache/
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    "user_permission": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "user_permission_cache",
    },
    "searchresults": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
}

# Hide nodes and cards in a report that have no data
HIDE_EMPTY_NODES_IN_REPORT = False

BYPASS_UNIQUE_CONSTRAINT_TILE_VALIDATION = False
BYPASS_REQUIRED_VALUE_TILE_VALIDATION = False

DATE_IMPORT_EXPORT_FORMAT = (
    "%Y-%m-%d"  # Custom date format for dates imported from and exported to csv
)

# This is used to indicate whether the data in the CSV and SHP exports should be
# ordered as seen in the resource cards or not.
EXPORT_DATA_FIELDS_IN_CARD_ORDER = False

# Identify the usernames and duration (seconds) for which you want to cache the time wheel
CACHE_BY_USER = {"default": 3600 * 24, "anonymous": 3600 * 24}  # 24hrs  # 24hrs

TILE_CACHE_TIMEOUT = 600  # seconds
CLUSTER_DISTANCE_MAX = 5000  # meters
GRAPH_MODEL_CACHE_TIMEOUT = None

OAUTH_CLIENT_ID = ""  #'9JCibwrWQ4hwuGn5fu2u1oRZSs9V6gK8Vu8hpRC4'

APP_TITLE = "Arches | Heritage Data Management"
COPYRIGHT_TEXT = "All Rights Reserved."
COPYRIGHT_YEAR = "2019"

ENABLE_CAPTCHA = False
# RECAPTCHA_PUBLIC_KEY = ''
# RECAPTCHA_PRIVATE_KEY = ''
# RECAPTCHA_USE_SSL = False
NOCAPTCHA = True
# RECAPTCHA_PROXY = 'http://127.0.0.1:8000'

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  #<-- Only need to uncomment this for testing without an actual email server
# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = "xxxx@xxx.com"
# EMAIL_HOST_PASSWORD = 'xxxxxxx'
# EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

CELERY_BROKER_URL = ""  # RabbitMQ --> "amqp://guest:guest@localhost",  Redis --> "redis://localhost:6379/0"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_BACKEND = (
    "django-db"  # Use 'django-cache' if you want to use your cache as your backend
)
CELERY_TASK_SERIALIZER = "json"


CELERY_SEARCH_EXPORT_EXPIRES = 24 * 3600  # seconds
CELERY_SEARCH_EXPORT_CHECK = 3600  # seconds

CELERY_BEAT_SCHEDULE = {
    "delete-expired-search-export": {
        "task": "arches.app.tasks.delete_file",
        "schedule": CELERY_SEARCH_EXPORT_CHECK,
    },
    "notification": {
        "task": "arches.app.tasks.message",
        "schedule": CELERY_SEARCH_EXPORT_CHECK,
        "args": ("Celery Beat is Running",),
    },
}

# Set to True if you want to send celery tasks to the broker without being able to detect celery.
# This might be necessary if the worker pool is regulary fully active, with no idle workers, or if
# you need to run the celery task using solo pool (e.g. on Windows). You may need to provide another
# way of monitoring celery so you can detect the background task not being available.
CELERY_CHECK_ONLY_INSPECT_BROKER = False

CANTALOUPE_DIR = os.path.join(ROOT_DIR, UPLOADED_FILES_DIR)
CANTALOUPE_HTTP_ENDPOINT = "http://localhost:8182/"

ACCESSIBILITY_MODE = False

BASEMAPS = [
    {
        "name": "positron",
        "title": "Light",
        "url": "https://tiles.openfreemap.org/styles/positron",
        "attribution": "Tiles by <a href='https://www.openfreemap.org/'>Open Free Map</a>",
        "addtomap": True,
        "type": "xyz",
        "iconclass": "fa fa-map",
    },
    {
        "name": "liberty",
        "title": "Streets",
        "url": "https://tiles.openfreemap.org/styles/liberty",
        "attribution": "Tiles by <a href='https://www.openfreemap.org/'>Open Free Map</a>",
        "addtomap": False,
        "type": "xyz",
        "iconclass": "fa fa-map",
    },
]

RENDERERS = [
    {
        "name": "imagereader",
        "title": "Image Reader",
        "description": "Displays most image file types",
        "id": "5e05aa2e-5db0-4922-8938-b4d2b7919733",
        "iconclass": "fa fa-camera",
        "component": "views/components/cards/file-renderers/imagereader",
        "ext": "",
        "type": "image/*",
        "exclude": "tif,tiff,psd",
    },
    {
        "name": "pdfreader",
        "title": "PDF Reader",
        "description": "Displays pdf files",
        "id": "09dec059-1ee8-4fbd-85dd-c0ab0428aa94",
        "iconclass": "fa fa-file",
        "component": "views/components/cards/file-renderers/pdfreader",
        "ext": "pdf",
        "type": "application/pdf",
        "exclude": "tif,tiff,psd",
    },
]

# By setting RESTRICT_MEDIA_ACCESS to True, media file requests outside of Arches will checked against nodegroup permissions.
RESTRICT_MEDIA_ACCESS = False

# By setting RESTRICT_CELERY_EXPORT_FOR_ANONYMOUS_USER to True, if the user is attempting
# to export search results above the SEARCH_EXPORT_IMMEDIATE_DOWNLOAD_THRESHOLD
# value and is not signed in with a user account then the request will not be allowed.
RESTRICT_CELERY_EXPORT_FOR_ANONYMOUS_USER = False

# Dictionary containing any additional context items for customising email templates
EXTRA_EMAIL_CONTEXT = {
    "salutation": _("Hi"),
    "expiration": (
        datetime.now() + timedelta(seconds=CELERY_SEARCH_EXPORT_EXPIRES)
    ).strftime("%A, %d %B %Y"),
}

# see https://docs.djangoproject.com/en/1.9/topics/i18n/translation/#how-django-discovers-language-preference
# to see how LocaleMiddleware tries to determine the user's language preference
# (make sure to check your accept headers as they will override the LANGUAGE_CODE setting!)
# also see get_language_from_request in django.utils.translation.trans_real.py
# to see how the language code is derived in the actual code

####### TO GENERATE .PO FILES DO THE FOLLOWING ########
# run the following commands
# language codes used in the command should be in the form (which is slightly different
# form the form used in the LANGUAGE_CODE and LANGUAGES settings below):
# --local={countrycode}_{REGIONCODE} <-- countrycode is lowercase, regioncode is uppercase, also notice the underscore instead of hyphen
# commands to run (to generate files for "British English, German, and Spanish"):
# django-admin.py makemessages --ignore=env/* --local=de --local=en --local=en_GB --local=es  --extension=htm,py
# django-admin.py compilemessages


# default language of the application
# language code needs to be all lower case with the form:
# {langcode}-{regioncode} eg: en, en-gb ....
# a list of language codes can be found here http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

# list of languages to display in the language switcher,
# if left empty or with a single entry then the switch won't be displayed
# language codes need to be all lower case with the form:
# {langcode}-{regioncode} eg: en, en-gb ....
# a list of language codes can be found here http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGES = [
    ("fr", "French"),
    ("en", "English"),
    ("de", "German"),
    ("pt", "Portuguese"),
]

# override this to permenantly display/hide the language switcher
SHOW_LANGUAGE_SWITCH = len(LANGUAGES) > 1

COLLECTIONS_GRAPHID = "bda239c6-d376-11ef-a239-0275dc2ded29"

# Implement this class to associate custom documents to the ES resource index
# See tests.views.search_tests.TestEsMappingModifier class for example
# ES_MAPPING_MODIFIER_CLASSES = ["arches_rascolls.search.es_mapping_modifier.EsMappingModifier"]

try:
    from .package_settings import *
except ImportError:
    try:
        from package_settings import *
    except ImportError as e:
        pass

try:
    from .settings_local import *
except ImportError as e:
    try:
        from settings_local import *
    except ImportError as e:
        pass
