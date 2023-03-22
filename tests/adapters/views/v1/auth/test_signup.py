import datetime

import pytest
import sqlalchemy as sa
from backend import consts
from backend import settings
from backend import texts
from backend.adapters import models

pytestmark = pytest.mark.asyncio


class TestSignUp:
    URL = "/api/v1/auth/signup/"

    @pytest.mark.usefixtures("mock_sms_service")
    async def test_post_success(self, client, session, clear_db_tables):
        response = await client.post(
            path=self.URL,
            json={
                "phone": settings.ADMIN_PHONE,
                "password": "12345678",
                "nickname": "John",
            },
        )
        response_data = response.json()
        assert response.status_code == 201, response_data
        assert isinstance(response_data["id"], int)

        patient = await session.get(
            models.Patient,
            response_data["id"],
            options=[
                sa.orm.joinedload(models.Patient.sex),
                sa.orm.joinedload(models.Patient.diagnosis),
                sa.orm.joinedload(models.Patient.phone),
            ],
            populate_existing=True,
        )
        assert not await patient.check_credential_confirmed(session)
        assert patient.first_name == "John"
        assert patient.birth_date == datetime.date(1980, 1, 2)
        assert patient.diagnosis.name == "t92_0"
        assert patient.sex.name == "male"
        await clear_db_tables([models.Patient, models.Phone], session)

    @pytest.mark.usefixtures("mock_sms_service")
    async def test_post_patient_with_confirmed_phone_fail(
        self,
        client,
        confirmed_phone,
    ):
        response = await client.post(
            path=self.URL,
            json={
                "phone": confirmed_phone.number,
                "password": "12345678",
                "first_name": "John",
                "middle_name": "Tuturutu",
                "last_name": "Sina",
                "birth_date": "1980-01-02",
                "diagnosis_id": consts.Diagnosis.T92_0,
                "sex_id": consts.Sex.MALE,
            },
        )
        response_data = response.json()
        assert response.status_code == 422, response_data
        assert response_data["detail"]["msg"] == texts.ALREADY_EXISTS
