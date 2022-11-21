import abc
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Case(abc.ABC):

    @abc.abstractmethod
    async def execute(self, *args, **kwargs):
        pass


@dataclass
class CaseDB(Case):
    session: AsyncSession
