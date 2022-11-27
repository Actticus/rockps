import fastapi
import jose
import sqlalchemy.ext.asyncio as sa_asyncio
from fastapi import security
from jose import jwt

from rockps import settings
from rockps import texts
from rockps.adapters import models
from rockps.adapters import sessions

OAUTH2_SCHEME = security.OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign_in")


async def get_user(
    token: str = fastapi.Depends(OAUTH2_SCHEME),
    session: sa_asyncio.AsyncSession = fastapi.Depends(
        sessions.create_session
    ),
):
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail=texts.COULD_NOT_VALIDATE_CREDITS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jose.JWTError:
        raise credentials_exception  # pylint: disable=raise-missing-from
    if (user_id := payload.get("sub")) is None:
        raise credentials_exception
    if not user_id.isdigit():
        raise credentials_exception
    if (user := await session.get(models.User, int(user_id))) is None:
        raise credentials_exception
    return user


async def get_confirmed_user(
    user: models.User = fastapi.Depends(get_user),
    session: sa_asyncio.AsyncSession = fastapi.Depends(
        sessions.create_session
    ),
):
    phone = await session.get(models.Phone, user.phone_id)
    if not phone.is_confirmed:
        raise fastapi.HTTPException(
            status_code=400,
            detail=texts.UNCONFIRMED_USER,
        )
    return user


async def validate_allowed_to_user(
    requesting_user,
    user_id,
    loc,
    user_msg,
):
    field = loc[1]

    if requesting_user.id != user_id:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "loc": loc,
                "msg": user_msg,
                "type": f"validation_error.{field}",
            },
        )
