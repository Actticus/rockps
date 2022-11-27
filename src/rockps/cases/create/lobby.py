from dataclasses import dataclass

from rockps import entities
from rockps.cases import mixins
from rockps.cases.create import base


@dataclass
class CreateLobby(base.Create, mixins.ValidatePhone):

    async def validate(self):
        pass

    async def create(self) -> entities.IModel:
        password = self.data.pop('password', None)
        obj = await super().create()
        if password:
            obj.set_password(password)
        await self.session.flush()
        await self.session.refresh(obj)

        return obj
