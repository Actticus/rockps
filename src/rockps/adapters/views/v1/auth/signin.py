import fastapi
from fastapi import security
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import cases
from rockps.adapters import models
from rockps.adapters import sessions
from rockps.adapters.views import schemes


class SignIn:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/", response_model=schemes.SuccessSignIn)
    async def post(
        form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
        session: AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        case = cases.auth.SignIn(
            session=session,
            phone_model=models.Phone,
            user_model=models.User,
            data={
                "phone": form_data.username,
                "password": form_data.password,
            },
        )

        user: models.User = await case.execute()
        access_token = user.create_access_token()
        return {
            "user": schemes.UserGet.from_orm(user),
            "access_token": access_token,
            "token_type": "bearer"
        }
