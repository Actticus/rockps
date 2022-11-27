from dataclasses import dataclass

from rockps import entities
from rockps.cases import abstract


@dataclass
class Create(abstract.CaseDB):
    model: entities.IModel
    data: dict

    async def create(self) -> entities.IModel:
        obj = self.model(**self.data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj, ["id"])
        return obj

    async def execute(self, *args, **kwargs) -> entities.IModel:
        return await self.create()
