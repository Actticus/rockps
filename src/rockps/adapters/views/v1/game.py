import fastapi
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps import cases
from rockps import consts
from rockps import texts
from rockps.adapters import models
from rockps.adapters import sessions
from rockps.adapters.views import schemes
from rockps.adapters.views.v1 import access


class Game:
    router = fastapi.APIRouter()

    @staticmethod
    @router.patch("/", response_model=schemes.Identifier)
    async def patch(
        game_data: schemes.GamePatch,
        requesting_user: models.User = fastapi.Depends(
            access.get_confirmed_user,
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        if not requesting_user.current_lobby_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=texts.USER_NOT_IN_LOBBY,
            )

        result = await session.execute(
            sa.select(
                models.Game,
            ).where(
                models.Game.lobby_id == requesting_user.current_lobby_id,
            )
        )

        games = result.scalars().all()
        active_game = None
        next_game = None
        for game in games:
            if game.game_status_id == consts.GameStatus.ACTIVE.value:
                active_game = game
                continue
            if active_game:
                next_game = game
                break

        if not active_game:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=texts.NO_ACTIVE_GAME,
            )

        case = cases.UpdateGame(
            model=models.Game,
            data={
                "user_id": requesting_user.id,
                "game_id": active_game.id,
                "next_game_id": next_game.id if next_game else None,
                "creator_id": active_game.creator_id,
                "player_id": active_game.player_id,
                "creator_card_id": active_game.creator_card_id,
                "player_card_id": active_game.player_card_id,
                "game_type_id": active_game.game_type_id,
                "user_card_id": game_data.card_id,
            },
            session=session,
        )
        game = await case.execute()
        return {"id": game.id}

    @staticmethod
    @router.get("/", response_model=list[schemes.GameGet])
    async def get(
        requesting_user: models.User = fastapi.Depends(
            access.get_confirmed_user
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        if not requesting_user.current_lobby_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=texts.USER_NOT_IN_LOBBY,
            )

        result = await session.execute(
            sa.select(
                models.Game
            ).where(
                models.Game.lobby_id ==
                    requesting_user.current_lobby_id,
            ).order_by(
                models.Game.id,
            )
        )
        games = result.unique().scalars().all()

        formatted_games = []
        for game in games:
            formatted_game = {
                "id": game.id,
                "game_status": game.game_status_id,
                "creator_id": game.creator_id,
                "player_id": game.player_id,
                "opponent_ready": False,
            }

            if game.game_status_id == consts.GameStatus.ACTIVE.value and \
                    requesting_user.id == game.creator_id:
                formatted_game["creator_card"] = game.creator_card_id
                formatted_game["player_card"] = None
                if game.player_card_id:
                    formatted_game["opponent_ready"] = True
            elif game.game_status_id == consts.GameStatus.ACTIVE.value and \
                    requesting_user.id == game.player_id:
                formatted_game["creator_card"] = None
                formatted_game["player_card"] = game.player_card_id
                if game.creator_card_id:
                    formatted_game["opponent_ready"] = True
            else:
                formatted_game["creator_card"] = game.creator_card_id
                formatted_game["player_card"] = game.player_card_id
                formatted_game["opponent_ready"] = True
            formatted_games.append(formatted_game)

        return formatted_games
