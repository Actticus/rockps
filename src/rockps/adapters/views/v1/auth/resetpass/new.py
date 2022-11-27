import fastapi
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps import cases
from rockps.adapters import models
from rockps.adapters import sessions
from rockps.adapters.views import schemes


class ResetPasswordNew:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/", response_model=schemes.Identifier, status_code=200)
    async def post(
        new: schemes.NewPassword,
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        case = cases.auth.ResetPasswordNew(
            session=session,
            certificate_model=models.Certificate,
            data=new.dict(),
        )
        user = await case.execute()
        return {"id": user.id}
