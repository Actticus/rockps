import httpx
import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import consts
from rockps import texts
from rockps.adapters import models

pytestmark = pytest.mark.asyncio


class TestGame:
    URL = "/api/v1/game/"

    async def test_get_empty_game_success(
        self,
        client: httpx.AsyncClient,
        user: models.User,
        lobby: models.Lobby,
        session: AsyncSession,
    ):
        response = await client.get(
            url=self.URL,
            headers={
                "Authorization": f"Bearer {user.create_access_token()}"
            }
        )
        response_data = response.json()
        assert response.status_code == 200, response_data

        result = await session.execute(
            sa.select(
                models.Game,
            ).where(
                models.Game.lobby_id == lobby.id,
            ).order_by(
                models.Game.id,
            )
        )
        games = result.scalars().all()

        assert len(response_data) == len(games)
        for game, game_data in zip(games, response_data):
            assert game_data["id"] == game.id
            assert game_data["lobby_id"] == game.lobby_id
            assert game_data["creator_id"] == game.creator_id
            assert game_data["player_id"] == game.player_id
            assert game_data["creator_card_id"] == game.creator_card_id
            assert game_data["player_card_id"] == game.player_card_id
            assert game_data["game_status_id"] == game.game_status_id
            assert game_data["opponent_ready"] is None
            assert game_data["opponent_nickname"] is None

    async def test_patch_make_move_success(
        self,
        client: httpx.AsyncClient,
        user: models.User,
        second_user: models.User,
        lobby: models.Lobby,
        session: AsyncSession,
    ):
        pass
