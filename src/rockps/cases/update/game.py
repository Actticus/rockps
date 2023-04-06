from dataclasses import dataclass

import fastapi
import loguru
import sqlalchemy as sa

from rockps import consts
from rockps import texts
from rockps.cases.update import base


@dataclass
class UpdateGame(base.Update):
    async def validate(self):
        await super().validate()
        if (self.data["user_id"] == self.data["creator_id"] and
                self.data["creator_card_id"] or self.data["player_card_id"] and
                self.data["user_id"] == self.data["player_id"]):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=[{
                    "loc": ["body"],
                    "msg": texts.USER_ALREADY_PLAYED_CARD,
                    "type": "validation_error",
                }],
            )
        if (self.data["game_type_id"] == consts.GameType.STANDARD and
                self.data["user_card_id"] > consts.Card.SCISSORS):
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=[{
                    "loc": ["body"],
                    "msg": texts.INVALID_CARD,
                    "type": "validation_error",
                }],
            )

    @staticmethod
    async def calculate_game_result(
        creator_card_id: int,
        creator_id: int,
        player_card_id: int,
        player_id: int,
    ) -> int | None:
        if player_card_id == creator_card_id:
            return None
        # pylint: disable=line-too-long,too-many-boolean-expressions
        if (player_card_id == consts.Card.ROCK and creator_card_id == consts.Card.SCISSORS) or \
                (player_card_id == consts.Card.SCISSORS and creator_card_id == consts.Card.PAPER) or \
                (player_card_id == consts.Card.PAPER and creator_card_id == consts.Card.ROCK) or \
                (player_card_id == consts.Card.ROCK and creator_card_id == consts.Card.LIZARD) or \
                (player_card_id == consts.Card.LIZARD and creator_card_id == consts.Card.SPOCK) or \
                (player_card_id == consts.Card.SPOCK and creator_card_id == consts.Card.SCISSORS) or \
                (player_card_id == consts.Card.SCISSORS and creator_card_id == consts.Card.LIZARD) or \
                (player_card_id == consts.Card.LIZARD and creator_card_id == consts.Card.PAPER) or \
                (player_card_id == consts.Card.PAPER and creator_card_id == consts.Card.SPOCK) or \
                (player_card_id == consts.Card.SPOCK and creator_card_id == consts.Card.ROCK):
            return player_id
        return creator_id

    async def update(self):
        user_id = self.data.pop("user_id")
        self.obj = await self.session.get(self.model, self.data["id"])
        if user_id == self.data["creator_id"]:
            self.data["creator_card_id"] = self.data.pop("user_card_id")
        if user_id == self.data["player_id"]:
            self.data["player_card_id"] = self.data.pop("user_card_id")

        if self.data["creator_card_id"] and self.data["player_card_id"]:
            self.data["game_status_id"] = consts.GameStatus.FINISHED.value

            score = {
                None: 0,  # Draw
                self.data["creator_id"]: 0,
                self.data["player_id"]: 0,
            }
            self.data["winner_id"] = await self.calculate_game_result(
                creator_card_id=self.data["creator_card_id"],
                creator_id=self.data["creator_id"],
                player_card_id=self.data["player_card_id"],
                player_id=self.data["player_id"],
            )
            score[self.data["winner_id"]] += 1

            result = await self.session.execute(
                sa.select(
                    self.model,
                ).where(
                    self.model.lobby_id == self.data["id"],
                ).order_by(
                    self.model.id,
                )
            )
            games = result.scalars().all()

            next_game_id = 0
            for i, game in enumerate(games):
                if next_game_id >= i:
                    del score[None]
                    if max(score.values()) > len(games) / 2:
                        game.game_status_id = consts.GameStatus.FINISHED.value
                        self.session.add(game)
                    else:
                        game.game_status_id = consts.GameStatus.ACTIVE.value
                        self.session.add(game)
                        next_game_id = 0
                        break

                if game.id != self.data["id"]:
                    score[game.winner_id] += 1
                else:
                    next_game_id = i + 1

            if max(score.values()) > len(games) / 2 or next_game_id == 0:
                lobby = await self.session.get(
                    self.model,
                    self.data["lobby_id"],
                )
                lobby.lobby_status_id = consts.LobbyStatus.FINISHED.value
                self.session.add(lobby)
        await super().update()
