import httpx

from rockps.adapters import models


class TestUser:
    URL = "/api/v1/user"

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

        assert response_data["id"] == user.id
        assert response_data["nickname"] == user.nickname
        assert response_data["current_lobby_id"] == lobby.id
