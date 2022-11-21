from abc import abstractmethod
from dataclasses import dataclass

from rockps.cases import abstract


@dataclass
class BaseAuth(abstract.CaseDB):
    data: dict

    @abstractmethod
    async def execute(self, *args, **kwargs):
        pass
