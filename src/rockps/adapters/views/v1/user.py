import fastapi

from rockps.adapters import models
from rockps.adapters.views import schemes
from rockps.adapters.views.v1 import access


class User:
    router = fastapi.APIRouter()

    @staticmethod
    @router.get("/", response_model=schemes.UserGet)
    async def get(
        requesting_user: models.User = fastapi.Depends(
            access.get_confirmed_user
        ),
    ):
        return schemes.UserGet.from_orm(requesting_user)
