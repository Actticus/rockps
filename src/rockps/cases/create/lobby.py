from dataclasses import dataclass

import sqlalchemy as sa
from backend import entities
from backend.cases import mixins
from backend.cases.create import base


@dataclass
class CreateLobby(base.Create, mixins.ValidatePhone):

    async def validate(self):
        pass

    async def create(self) -> entities.IModel:
        if number := self.data.pop("phone"):
            self.data["phone"] = self.phone_model(
                number=number,
                patient=None
            )
            self.session.add(self.data["phone"])
        obj = await super().create()
        await self.session.flush()
        await self.session.refresh(obj)

        return obj
