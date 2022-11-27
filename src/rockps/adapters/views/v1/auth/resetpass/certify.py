import uuid

import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps import cases
from rockps.adapters import models
from rockps.adapters import services
from rockps.adapters import sessions
from rockps.adapters.views import schemes


class Certificate(schemes.Identifier):
    certificate: uuid.UUID


class ResetPasswordCertify:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/", response_model=Certificate)
    async def post(
        code: schemes.ConfirmationCode,
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        case = cases.auth.ResetPasswordCertify(
            session=session,
            confirmation_code_model=models.ConfirmationCode,
            certificate_model=models.Certificate,
            phone_model=models.Phone,
            call_service=services.external.call,
            data=code.dict(),
        )
        result = await case.execute()
        return {
            "id": result["user"].id,
            "certificate": result["certificate"].id,
        }
