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

    async def test_patch_join_success(
        self,
        client: httpx.AsyncClient,
        user: models.User,
        lobby: models.Lobby,
        second_user: models.User,
        session: AsyncSession,
    ):
        response = await client.patch(
            url=self.URL,
            json={
                "id": lobby.id,
                "lobby_action_id": consts.LobbyAction.JOIN,
            },
            headers={
                "Authorization": f"Bearer {second_user.create_access_token()}"
            }
        )
        response_data = response.json()
        assert response.status_code == 200, response_data

        lobby = await session.get(
            models.Lobby,
            response_data["id"],
            populate_existing=True,
        )
        assert lobby.creator_id == user.id
        assert lobby.player_id == second_user.id

        await session.refresh(second_user)
        assert second_user.current_lobby_id == lobby.id

    async def test_patch_third_user_join_fail(
        self,
        client: httpx.AsyncClient,
        lobby: models.Lobby,
        second_user: models.User,
        third_user: models.User,
        session: AsyncSession,
    ):
        lobby.player_id = second_user.id
        lobby.lobby_status_id = consts.LobbyStatus.ACTIVE
        second_user.current_lobby_id = lobby.id
        await session.commit()

        response = await client.patch(
            url=self.URL,
            json={
                "id": lobby.id,
                "lobby_action_id": consts.LobbyAction.JOIN,
            },
            headers={
                "Authorization": f"Bearer {third_user.create_access_token()}"
            }
        )
        response_data = response.json()
        assert response.status_code == 403, response_data
        assert response_data["detail"][0]["msg"] == texts.LOBBY_ACCESS_DENIED
