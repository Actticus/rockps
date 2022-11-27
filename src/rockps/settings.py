import environs

env = environs.Env()
env.read_env(override=True)  # read .env file, if it exist

# Instance
SECRET_KEY = env.str("SECRET_KEY")

# Authorization
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 3
JWT_ALGORITHM = "HS256"

# Database
POSTGRES_USER = env.str("POSTGRES_USER")
POSTGRES_PASSWORD = env.str("POSTGRES_PASSWORD")
POSTGRES_DB = env.str("POSTGRES_DB")
DATABASE_ASYNC_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"  # pylint: disable=line-too-long
DATABASE_SYNC_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@127.0.0.1:5432/{POSTGRES_DB}"  # pylint: disable=line-too-long

# Services
ADMIN_PHONE = env.str("ADMIN_PHONE")

# External services
NEWTEL_API_KEY = env.str("NEWTEL_API_KEY")
NEWTEL_SIGNING_KEY = env.str("NEWTEL_SIGNING_KEY")
