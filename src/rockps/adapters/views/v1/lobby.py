import fastapi
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio
from sqlalchemy import orm

from rockps import cases
from rockps import consts
from rockps import texts
from rockps.adapters import models
from rockps.adapters import sessions
from rockps.adapters.views import schemes
from rockps.adapters.views.v1 import access


class Lobby:
    router = fastapi.APIRouter()

    @staticmethod
    @router.patch("/", response_model=schemes.LobbyGet)
    async def patch(
        lobby_data: schemes.LobbyPatch,
        requesting_user: models.User = fastapi.Depends(
            access.get_confirmed_user,
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        lobby_id = (lobby_data.id
                    if lobby_data.id
                    else requesting_user.current_lobby_id)
        if (lobby := await session.get(models.Lobby, lobby_id)) is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=texts.LOBBY_DOES_NOT_EXIST,
            )

        case = cases.UpdateLobby(
            model=models.Lobby,
            data={
                "user_id": requesting_user.current_lobby_id,
                "lobby_id": lobby_data.id,
                **lobby_data,
            },
            session=session,
        )
        lobby = await case.execute()
        return lobby

    @staticmethod
    @router.post("/", response_model=schemes.Identifier)
    async def post(
        lobby_data: schemes.LobbyPost,
        requesting_user: models.User = fastapi.Depends(
            access.get_confirmed_user,
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        if requesting_user.current_lobby_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=texts.USER_ALREADY_IN_LOBBY,
            )

        case = cases.CreateLobby(
            model=models.Lobby,
            game_model=models.Game,
            data={
                "creator_id": requesting_user.id,
                **lobby_data,
            },
            session=session,
        )
        lobby = await case.execute()
        return {"id": lobby.id}

    @staticmethod
    @router.get("/", response_model=schemes.Page[schemes.LobbyGet])
    async def get(
        _: schemes.UserGet = fastapi.Depends(
            access.get_confirmed_user
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
        offset: int = fastapi.Query(0, ge=0),
        limit: int = fastapi.Query(100, ge=1, le=1000),
    ):
        result = await session.execute(
            sa.select(
                sa.func.count(models.Lobby.id)
            )
        )
        total = result.scalar()

        result = await session.execute(
            sa.select(
                models.Lobby,
            ).where(
                models.Lobby.lobby_status_id == consts.LobbyStatus.OPENED.value,
            ).order_by(
                models.Lobby.id,
            ).options(
                orm.joinedload(models.Lobby.users),
            ).offset(
                offset,
            ).limit(
                limit,
            )
        )
        lobbies = result.unique().scalars().all()
        return schemes.Page(
            items=[schemes.LobbyGet.from_orm(lobby) for lobby in lobbies],
            offset=offset,
            limit=limit,
            total=total,
        )
