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
        user_current_lobby_id = self.data.pop("user_current_lobby_id", None)
        if (user_current_lobby_id != self.data["id"] and
                self.data["lobby_status_id"] != consts.LobbyStatus.OPENED):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=texts.LOBBY_ACCESS_DENIED,
            )
        if (user_current_lobby_id == self.data["id"] and
                self.data["lobby_action_id"] != consts.LobbyAction.LEAVE):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail=texts.USER_ALREADY_IN_LOBBY,
            )

    async def update(self):
        user_id = self.data.pop("user_id")
        lobby_action_id = self.data.pop("lobby_action_id")

        if lobby_action_id == consts.LobbyAction.LEAVE:
            self.data["lobby_status_id"] = consts.LobbyStatus.CANCELED.value

            user = await self.session.get(self.user_model, user_id)
            user.current_lobby_id = None
            self.session.add(user)

            result = await self.session.execute(
                sa.select(
                    self.game_model,
                ).where(
                    self.game_model.lobby_id == self.data["id"],
                )
            )
            games = result.scalars().all()
            for game in games:
                if (game.game_status_id == consts.GameStatus.ACTIVE.value or
                        game.game_status_id == consts.GameStatus.PENDING.value):
                    game.game_status_id = consts.GameStatus.CANCELED.value
                    self.session.add(game)
                    break

        elif lobby_action_id == consts.LobbyAction.JOIN:
            user = await self.session.get(self.user_model, user_id)
            user.current_lobby_id = self.data["id"]

            self.data["lobby_status_id"] = consts.LobbyStatus.ACTIVE.value
            self.session.add(user)

            games = [self.game_model(
                lobby_id=self.data["id"],
                creator_id=self.data["creator_id"],
                player_id=user_id,
                game_status_id=consts.GameStatus.ACTIVE.value,
                game_type_id=self.data["lobby_type_id"],
            )]
            for _ in range(self.data["max_games"] - 1):
                game = self.game_model(
                    lobby_id=self.data["id"],
                    creator_id=self.data["creator_id"],
                    player_id=user_id,
                    game_status_id=consts.GameStatus.PENDING.value,
                    game_type_id=self.data["lobby_type_id"],
                )
                games.append(game)
            self.session.add_all(games)

        await super().update()
