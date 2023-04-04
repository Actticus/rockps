from dataclasses import dataclass

import fastapi
import sqlalchemy as sa

from rockps import consts
from rockps import entities
from rockps import texts
from rockps.cases.update import base


@dataclass
class UpdateLobby(base.Update):
    user_model: entities.IModel
    game_model: entities.IModel

    async def validate(self):
        await super().validate()
        self.obj = await self.session.get(self.model, self.data.pop("id"))
        user_current_lobby_id = self.data.pop("user_current_lobby_id", None)
        detail = [{
            "loc": ["body"],
            "type": "validation_error",
        }]
        if (user_current_lobby_id != self.obj.id and
                self.data["lobby_status_id"] != consts.LobbyStatus.OPENED):
            detail[0]["msg"] = texts.LOBBY_ACCESS_DENIED
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=detail,
            )

        if (user_current_lobby_id == self.obj.id and
                self.data["lobby_action_id"] == consts.LobbyAction.JOIN):
            detail[0]["msg"] = texts.USER_ALREADY_IN_LOBBY
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=detail,
            )

    async def update(self):
        user_id = self.data.pop("user_id")
        lobby_action_id = self.data.pop("lobby_action_id")
        user = await self.session.get(self.user_model, user_id)

        if (lobby_action_id == consts.LobbyAction.LEAVE and
                self.data["lobby_status_id"] in
                (consts.LobbyStatus.OPENED, consts.LobbyStatus.ACTIVE)):
            self.data["lobby_status_id"] = consts.LobbyStatus.CANCELED.value

            user.current_lobby_id = None
            self.session.add(user)

            result = await self.session.execute(
                sa.select(
                    self.game_model,
                ).where(
                    self.game_model.lobby_id == self.obj.id,
                )
            )
            games = result.scalars().all()
            for game in games:
                if (game.game_status_id in
                        (consts.GameStatus.ACTIVE, consts.GameStatus.PENDING)):
                    game.game_status_id = consts.GameStatus.CANCELED.value
                    self.session.add(game)

        elif lobby_action_id == consts.LobbyAction.LEAVE:
            user.current_lobby_id = None
            self.session.add(user)

        elif lobby_action_id == consts.LobbyAction.JOIN:
            user.current_lobby_id = self.obj.id
            self.data["player_id"] = user_id
            self.data["lobby_status_id"] = consts.LobbyStatus.ACTIVE.value
            self.session.add(user)

            result = await self.session.execute(
                sa.select(
                    self.game_model,
                ).where(
                    self.game_model.lobby_id == self.obj.id,
                )
            )
            games = result.scalars().all()

            games[0].player_id = user_id
            games[0].game_status_id = consts.GameStatus.ACTIVE.value
            for game in games[1:]:
                game.player_id = user_id
                game.game_status_id = consts.GameStatus.PENDING.value
                self.session.add(game)

        await super().update()
