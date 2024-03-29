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

        creator = await self.session.get(self.user_model, lobby.creator_id)
        creator.current_lobby_id = lobby.id

        for _ in range(lobby.max_games):
            game = self.game_model(
                lobby_id=lobby.id,
                creator_id=lobby.creator_id,
                game_status_id=consts.GameStatus.PENDING.value,
                game_type_id=lobby.lobby_type_id,
            )
            self.session.add(game)

        self.session.add(creator)
        await self.session.flush()
        return lobby
