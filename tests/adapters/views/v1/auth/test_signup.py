import httpx
import pytest
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import settings
from rockps import texts
from rockps.adapters import models

pytestmark = pytest.mark.asyncio


class TestSignUp:
    URL = "/api/v1/auth/signup/"

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_success(
        self,
        client,
        session: AsyncSession,
    ):
        response = await client.post(
            url=self.URL,
            json={
                "phone": settings.ADMIN_PHONE,
                "password": "12345678",
                "nickname": "John",
            },
        )
        response_data = response.json()
        assert response.status_code == 201, response_data
        assert isinstance(response_data["id"], int)

        user: models.User = await session.get(
            models.User,
            response_data["id"],
            options=[
                sa_orm.joinedload(models.User.phone),
            ],
            populate_existing=True,
        )
        assert not user.phone.is_confirmed
        assert user.nickname == "John"
        phone = user.phone
        result = await session.execute(
            sa.select(
                models.ConfirmationCode,
            ).where(
                models.ConfirmationCode.phone_id == phone.id,
            ).execution_options(
                populate_existing=True,
            )
        )
        confirmation_code = result.scalars().first()
        await session.delete(confirmation_code)
        await session.delete(user)
        await session.delete(phone)
        await session.commit()

    @pytest.mark.usefixtures("mock_call_service")
    async def test_post_patient_with_confirmed_phone_fail(
        self,
        client: httpx.AsyncClient,
        confirmed_phone: models.Phone,
    ):
        response = await client.post(
            url=self.URL,
            json={
                "phone": confirmed_phone.number,
                "password": "12345678",
                "nickname": "John",
            },
        )
        response_data = response.json()
        assert response.status_code == 422, response_data
        assert response_data["detail"][0]["msg"] == texts.ALREADY_EXISTS
