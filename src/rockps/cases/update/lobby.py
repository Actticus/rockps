from dataclasses import dataclass

import fastapi

from rockps import consts
from rockps import entities
from rockps import texts
from rockps.cases.update import base


@dataclass
class UpdateLobby(base.Update):
    user_model: entities.IModel

    async def validate(self):
        await super().validate()
        lobby_user_ids = (self.data["creator_id"], self.data["player_id"])
        if (self.data["user_current_lobby_id"] != self.data["id"] and
                self.data["lobby_status_id"] != consts.LobbyStatus.OPENED):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=texts.LOBBY_ACCESS_DENIED,
            )
        if (self.data["user_current_lobby_id"] in lobby_user_ids and
                self.data["lobby_action_id"] != consts.LobbyAction.LEAVE):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=texts.LOBBY_ACCESS_DENIED,
            )

    async def update(self):

        await super().update()
