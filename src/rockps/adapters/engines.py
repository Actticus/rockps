from sqlalchemy.ext.asyncio import AsyncSession

from rockps import settings


class Database:
    _ENGINES = {}

    @classmethod
    def init(cls):
        default = sa_asyncio.create_async_engine(
            settings.DATABASE_ASYNC_URL,
        )
        cls._ENGINES['default'] = default

    @classmethod
    def get(cls, name='default'):
        return cls._ENGINES[name]
