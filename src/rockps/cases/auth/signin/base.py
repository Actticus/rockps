import abc
from dataclasses import dataclass

from rockps import entities
from rockps.cases import abstract


@dataclass
class BaseSignIn(abstract.CaseDB):
    data: dict

    @abc.abstractmethod
    async def validate(self):
        pass

    @abc.abstractmethod
    async def authenticate(self):
        pass

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        return await self.authenticate()
