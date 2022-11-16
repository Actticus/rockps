import abc
from dataclasses import dataclass

import sqlalchemy.ext.asyncio as sa_asyncio


@dataclass
class Case(abc.ABC):

    @abc.abstractmethod
    async def execute(self, *args, **kwargs):
        pass


@dataclass
class CaseDB(Case):
    session: sa_asyncio.AsyncSession
