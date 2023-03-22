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
        lobby_id = (requesting_user.current_lobby_id
                    if requesting_user.current_lobby_id
                    else lobby_data.id)
        if (lobby := await session.get(models.Lobby, lobby_id)) is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_404_NOT_FOUND,
                detail=texts.LOBBY_DOES_NOT_EXIST,
            )

        case = cases.UpdateLobby(
            model=models.Lobby,
            user_model=models.User,
            data={
                "user_id": requesting_user.id,
                "user_current_lobby_id": requesting_user.current_lobby_id,
                "id": lobby.id,
                "lobby_status_id": lobby.lobby_status_id,
                "creator_id": lobby.creator_id,
                "player_id": lobby.player_id,
                "lobby_action_id": lobby_data.lobby_action_id,
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
                **lobby_data.dict(),
            },
            session=session,
        )
        lobby = await case.execute()
        return {"id": lobby.id}

    @staticmethod
    @router.get("/", response_model=list[schemes.LobbyGet])
    async def get(
        _: schemes.UserGet = fastapi.Depends(
            access.get_confirmed_user
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),

    ):
        result = await session.execute(
            sa.select(
                models.Lobby,
            ).where(
                models.Lobby.lobby_status_id == consts.LobbyStatus.OPENED.value,
            ).order_by(
                models.Lobby.id,
            )
        )
        lobbies = result.unique().scalars().all()
        return [schemes.LobbyGet.from_orm(lobby) for lobby in lobbies]
