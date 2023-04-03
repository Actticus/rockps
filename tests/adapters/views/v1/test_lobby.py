import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import consts
from rockps import texts
from rockps.adapters import models

pytestmark = pytest.mark.asyncio


class TestLobby:
    URL = "/api/v1/lobby/"

    async def test_post_success(
        self,
        client: httpx.AsyncClient,
        user: models.User,
        session: AsyncSession,
    ):
        response = await client.post(
            url=self.URL,
            json={
                "name": "Best Lobby Ever",
                "max_games": 3,
                "lobby_type_id": consts.LobbyType.STANDARD,
            },
            headers={
                "Authorization": f"Bearer {user.create_access_token()}"
            }
        )
        response_data = response.json()
        assert response.status_code == 200, response_data

        lobby = await session.get(models.Lobby, response_data["id"])
        assert lobby.name == "Best Lobby Ever"

        await session.refresh(user)
        assert user.current_lobby_id == lobby.id

    async def test_post_even_max_games_fail(
        self,
        client: httpx.AsyncClient,
        user: models.User,
    ):
        response = await client.post(
            url=self.URL,
            json={
                "name": "Best Lobby Ever",
                "max_games": 2,
                "lobby_type_id": consts.LobbyType.EXTENDED,
            },
            headers={
                "Authorization": f"Bearer {user.create_access_token()}"
            }
        )

        response_data = response.json()
        assert response.status_code == 422, response_data
        assert response_data["detail"][0]["msg"] == texts.MAX_GAMES_MUST_BE_ODD

    async def test_get_success(
        self,
        client: httpx.AsyncClient,
        user: models.User,
        lobby: models.Lobby,
    ):
        response = await client.get(
            url=self.URL,
            headers={
                "Authorization": f"Bearer {user.create_access_token()}"
            }
        )
        response_data = response.json()
        assert response.status_code == 200, response_data

        assert response_data["id"] == lobby.id
        assert response_data["name"] == lobby.name
        assert response_data["max_games"] == lobby.max_games
        assert response_data["lobby_type_id"] == lobby.lobby_type_id

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
