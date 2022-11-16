import environs

env = environs.Env()
env.read_env(override=True)  # read .env file, if it exist

# Instance
# ========
DEBUG = env.bool("DEBUG")
SECRET_KEY = env.str("SECRET_KEY")
ENV = env.str("ENV")
URL = env.str("URL")
RAW_DATA_ENABLED = env.bool("RAW_DATA_ENABLED")
PID_FILE = "daemon_worker.pid"

# Authorization
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
JWT_ALGORITHM = "HS256"

# Database
DATABASE_ASYNC_URL = env.str("DATABASE_ASYNC_URL")
DATABASE_SYNC_URL = env.str("DATABASE_SYNC_URL")
REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.int("REDIS_PORT")

CLICKHOUSE_MIGRATION_URL = env.str("CLICKHOUSE_MIGRATION_URL")
CLICKHOUSE_HTTP_URL = env.str("CLICKHOUSE_HTTP_URL")
CLICKHOUSE_USER = env.str("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD = env.str("CLICKHOUSE_PASSWORD")

# Services
ADMIN_EMAIL = env.str("ADMIN_EMAIL")
ADMIN_PHONE = env.str("ADMIN_PHONE")

# External services
# =================
SENDGRID_API_KEY = env.str("SENDGRID_API_KEY")

NEWTEL_API_KEY = env.str("NEWTEL_API_KEY")
NEWTEL_SIGNING_KEY = env.str("NEWTEL_SIGNING_KEY")

SENTRY_URL = env.str("SENTRY_URL")
IS_SENTRY_SILENT = env.bool("IS_SENTRY_SILENT")

SBER_TEST_USERNAME = env.str("SBER_TEST_USERNAME")
SBER_TEST_PASSWORD = env.str("SBER_TEST_PASSWORD")
SBER_PROD_USERNAME = env.str("SBER_PROD_USERNAME")
SBER_PROD_PASSWORD = env.str("SBER_PROD_PASSWORD")
TELEGRAM_INSTALLMENT_BOT_CHAT_ID = env.str("TELEGRAM_INSTALLMENT_BOT_CHAT_ID")
TELEGRAM_INSTALLMENT_BOT_TOKEN = env.str("TELEGRAM_INSTALLMENT_BOT_TOKEN")

INIT_CONFIG = {
    "daemons_seconds": {
        "redis_secs": 5,
        "codes_expiring_secs": 60 * 60,  # 1 hour}
    }
}

# LOGGING
LOG_CONFIG = {
    "path": "/var/log/rockps.log",
    "level": env.str("LOG_LEVEL"),
    "rotation": "20 days",
    "retention": "1 months",
    "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level> <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    "loggers": ['uvicorn', 'uvicorn.error', 'fastapi'],
}
