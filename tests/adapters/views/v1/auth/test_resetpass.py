import bcrypt
import pytest

from rockps import texts
from rockps.adapters import models

pytestmark = pytest.mark.asyncio


class TestResetPassword:
    URL = "/api/v1/auth/reset-password/"

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_request_phone_success(self, client, user):
        response = await client.post(
            url=f"{self.URL}request/",
            json={"username": str(user.phone)},
        )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["id"] == user.id

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_request_wrong_phone_fail(self, client):
        response = await client.post(
            url=f"{self.URL}request/",
            json={"username": "79999999999"},  # without +
        )
        assert response.status_code == 422

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_request_unconfirmed_user_fail(
        self,
        client,
        unconfirmed_user,
    ):
        response = await client.post(
            url=f"{self.URL}request/",
            json={"username": str(unconfirmed_user.phone)},
        )
        response_data = response.json()
        assert response.status_code == 422
        assert response_data["detail"][0]["msg"] == texts.DOES_NOT_EXISTS

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_nonexistent_phone_fail(
        self,
        client,
    ):
        response = await client.post(
            url=f"{self.URL}request/",
            json={"username": "+71233455432"},
        )
        response_data = response.json()
        assert response.status_code == 422
        assert response_data["detail"][0]["msg"] == texts.DOES_NOT_EXISTS

    async def test_post_new_pass_success(self, client, certificate, session):
        new_password = "87654321"
        response = await client.post(
            url=f"{self.URL}new/",
            json={
                "certificate": str(certificate.id),
                "new_password": new_password,
            },
        )
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["id"] == certificate.user.id
        refreshed_user = await session.get(
            models.User,
            certificate.user.id,
            populate_existing=True,
        )
        assert bcrypt.checkpw(
            password=bytes(new_password, "ascii"),
            hashed_password=refreshed_user.password,
        )

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_certify_success(
        self,
        client,
        reset_code,
        session,
    ):
        response = await client.post(
            url=f"{self.URL}certify/",
            json={
                "username": str(reset_code.phone),
                "code": reset_code.value,
            },
        )
        response_data = response.json()
        assert response.status_code == 200, response_data
        user = await session.get(
            models.User,
            reset_code.phone.user.id,
            populate_existing=True,
        )
        assert response_data["id"] == user.id
        certificate = await session.get(
            models.Certificate,
            response_data["certificate"],
            populate_existing=True,
        )
        await session.delete(certificate)
        await session.commit()
        print()
