from dataclasses import dataclass

import fastapi

from rockps import consts
from rockps import texts
from rockps.cases.update import base


@dataclass
class UpdateLobby(base.Update):
    async def validate(self):
        await super().validate()

    async def update(self):

        await super().update()
