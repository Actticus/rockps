from dataclasses import dataclass

import sqlalchemy as sa

from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class Update(abstract.CaseDB, mixins.ValidateObject):
    model: entities.IModel
    data: dict

    def __post_init__(self):
        self.obj = None

    async def validate(self):
        pass

    async def update(self):
        obj = self.model(**self.data)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(self.obj)

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        await self.update()
        return self.obj
