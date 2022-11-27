import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps import cases
from rockps.adapters import models
from rockps.adapters import services
from rockps.adapters import sessions
from rockps.adapters.views import schemes


class Confirm:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/", response_model=schemes.Identifier)
    async def post(
        code: schemes.ConfirmationCode,
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        case = cases.auth.Confirm(
            confirmation_code_model=models.ConfirmationCode,
            call_service=services.external.call,
            phone_model=models.Phone,
            data=code.dict(),
            session=session,
        )
        user = await case.execute()
        return {"id": user.id}
