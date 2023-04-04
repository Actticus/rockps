from dataclasses import dataclass

import fastapi

from rockps import consts
from rockps import texts
from rockps.cases.update import base


@dataclass
class UpdateGame(base.Update):
    async def validate(self):
        await super().validate()
        detail = [{
            "loc": ["body", "user_card_id"],
            "msg": texts.USER_ALREADY_PLAYED_CARD,
            "type": "validation_error",
        }]
        if (self.data["user_id"] == self.data["creator_id"] and
                self.data["creator_card_id"]):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=detail,
            )
        if (self.data["user_id"] == self.data["player_id"] and
                self.data["player_card_id"]):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=detail,
            )
        if (self.data["game_type_id"] == consts.GameType.EXTENDED and
                self.data["user_card_id"] > consts.Card.SCISSORS.value):
            detail[0]["msg"] = texts.INVALID_CARD
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=detail,
            )

    async def update(self):
        user_id = self.data.pop("user_id")
        if user_id == self.data["creator_id"]:
            self.data["creator_card_id"] = self.data.pop("user_card_id")
        if user_id == self.data["player_id"]:
            self.data["player_card_id"] = self.data.pop("user_card_id")
        if self.data["creator_card_id"] and self.data["player_card_id"]:
            self.data["game_status_id"] = consts.GameStatus.FINISHED.value
            if next_game_id := self.data.pop("next_game_id", None):
                next_game = self.session.get(self.model, next_game_id)
                next_game.game_status_id = consts.GameStatus.ACTIVE.value
                self.session.add(next_game)
            else:
                lobby = self.session.get(self.model, self.data["lobby_id"])
                lobby.lobby_status_id = consts.LobbyStatus.FINISHED.value
                self.session.add(lobby)
        await super().update()
