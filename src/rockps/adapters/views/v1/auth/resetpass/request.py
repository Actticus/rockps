import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps import cases
from rockps.adapters import models
from rockps.adapters import services
from rockps.adapters import sessions
from rockps.adapters.views import schemes


class ResetPassRequest:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/", response_model=schemes.Identifier, status_code=200)
    async def post(
        req: schemes.ResetPasswordRequest,
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        case = cases.auth.ResetPasswordRequest(
            session=session,
            call_service=services.external.call,
            confirmation_code_model=models.ConfirmationCode,
            phone_model=models.Phone,
            data=req.dict(),
        )

        user = await case.execute()
        return {"id": user.id}
