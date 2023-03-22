from dataclasses import dataclass

from rockps import consts
from rockps import entities
from rockps.cases import mixins
from rockps.cases.create import base


@dataclass
class CreateLobby(base.Create, mixins.ValidatePhone):
    game_model: entities.IModel
    user_model: entities.IModel

    async def validate(self):
        pass

    async def create(self) -> entities.IModel:
        lobby = await super().create()

        games = []
        for _ in range(lobby.max_games):
            games.append(
                self.game_model(
                    lobby_id=lobby.id,
                    creator_id=lobby.creator_id,
                    player_id=None,
                    creator_card_id=None,
                    player_card_id=None,
                    game_status_id=consts.GameStatus.PENDING.value,
                    game_type_id=lobby.lobby_type_id,
                )
            )
        self.session.add_all(games)

        creator = await self.session.get(self.user_model, lobby.creator_id)
        creator.current_lobby_id = lobby.id
        self.session.add(creator)
        self.session.flush()
        return lobby
