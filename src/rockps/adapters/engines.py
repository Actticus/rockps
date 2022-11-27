from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine

from rockps import settings


class Database:
    _ENGINE: AsyncEngine

    @classmethod
    def init(cls):
        cls._ENGINE = create_async_engine(settings.DATABASE_ASYNC_URL)

    @classmethod
    def get(cls):
        return cls._ENGINE
