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
        if (self.data["user_current_lobby_id"] != self.data["id"] and
                self.data["lobby_status_id"] != consts.LobbyStatus.OPENED):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=texts.LOBBY_ACCESS_DENIED,
            )
        if (self.data["user_current_lobby_id"] == self.data["id"] and
                self.data["lobby_action_id"] != consts.LobbyAction.LEAVE):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=texts.USER_ALREADY_IN_LOBBY,
            )

    async def update(self):
        user_id = self.data.pop("user_id")
        lobby_action_id = self.data.pop("lobby_action_id")
        self.data.pop("user_current_lobby_id")
        if lobby_action_id == consts.LobbyAction.LEAVE:
            self.data["lobby_status_id"] = consts.LobbyStatus.CANCELED.value
            user = await self.session.get(self.user_model, user_id)
            user.current_lobby_id = None
            self.session.add(user)
        elif lobby_action_id == consts.LobbyAction.JOIN:
            user = await self.session.get(self.user_model, user_id)
            user.current_lobby_id = self.data["id"]
            self.data["lobby_status_id"] = consts.LobbyStatus.ACTIVE.value
            self.session.add(user)
        await super().update()
