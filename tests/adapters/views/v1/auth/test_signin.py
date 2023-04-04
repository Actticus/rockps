import pytest
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import settings
from rockps import texts
from rockps.adapters import models

pytestmark = pytest.mark.asyncio


class TestSignIn:
    URL = "/api/v1/auth/signin/"

    @pytest.mark.usefixtures("user")
    async def test_post_success(self, client, session: AsyncSession):
        form = {"username": settings.ADMIN_PHONE, "password": "qwerty123"}
        response = await client.post(
            url=self.URL,
            data=form,
        )
        response_data = response.json()
        assert response.status_code == 200, response_data
        payload = jwt.decode(
            response_data["access_token"],
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = int(payload.get("sub"))
        assert user_id == response_data["user"]["id"]
        user = await session.get(models.User, user_id)
        assert user.id == user_id

    @pytest.mark.usefixtures("user")
    async def test_post_wrong_password_fail(self, client):
        form = {"username": settings.ADMIN_PHONE, "password": "qwerty1234"}
        response = await client.post(
            url=self.URL,
            data=form,
        )
        response_data = response.json()
        assert response.status_code == 401, response_data

    async def test_post_sign_in_without_user_fail(
        self,
        client,
        admin_phone: models.Phone,
    ):
        form = {"username": admin_phone.number, "password": "qwerty1234"}
        response = await client.post(
            url=self.URL,
            data=form,
        )
        response_data = response.json()
        assert response.status_code == 422, response_data
        assert response_data["detail"][0]["msg"] == \
            texts.PHONE_USER_DOES_NOT_EXIST
