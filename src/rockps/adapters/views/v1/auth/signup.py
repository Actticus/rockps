import fastapi
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import cases
from rockps.adapters import models
from rockps.adapters import services
from rockps.adapters import sessions
from rockps.adapters.views import schemes


class SignUp:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/", response_model=schemes.Identifier, status_code=201)
    async def post(
        user_data: schemes.UserSignUp,
        session: AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        case = cases.auth.SignUp(
            call_service=services.external.call,
            session=session,
            phone_model=models.Phone,
            user_model=models.User,
            confirmation_code_model=models.ConfirmationCode,
            data=user_data.dict(),
        )
        user: models.User = await case.execute()
        return {"id": user.id}
