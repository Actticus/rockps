import fastapi
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio
from sqlalchemy import orm as sa_orm

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
        game = await session.get(models.Game, game_data.id)
        if requesting_user.current_lobby_id != game.lobby_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=[{
                    "loc": ["body"],
                    "msg": texts.USER_NOT_IN_LOBBY,
                    "type": "validation_error",
                }],
            )
        if game.game_status_id != consts.GameStatus.ACTIVE.value:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=[{
                    "loc": ["body"],
                    "msg": texts.GAME_NOT_ACTIVE,
                    "type": "validation_error",
                }],
            )

        case = cases.UpdateGame(
            model=models.Game,
            data={
                "id": game_data.id,
                "user_id": requesting_user.id,
                "creator_id": game.creator_id,
                "creator_card_id": game.creator_card_id,
                "player_id": game.player_id,
                "player_card_id": game.player_card_id,
                "lobby_id": game.lobby_id,
                "user_card_id": game_data.card_id,
                "game_type_id": game.game_type_id,
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
                detail=[{
                    "loc": ["body"],
                    "msg": texts.USER_NOT_IN_LOBBY,
                    "type": "validation_error",
                }],
            )

        result = await session.execute(
            sa.select(
                models.Game,
            ).where(
                models.Game.lobby_id == requesting_user.current_lobby_id,
            ).order_by(
                models.Game.id,
            ).options(
                sa_orm.joinedload(models.Game.creator),
                sa_orm.joinedload(models.Game.player),
            )
        )
        games = result.scalars().all()

        user_is_creator = requesting_user.id == games[0].creator_id
        if not user_is_creator:
            opponent_nickname = games[0].creator.nickname
        elif games[0].player:
            opponent_nickname = games[0].player.nickname
        else:
            opponent_nickname = None

        formatted_games = []
        for game in games:
            formatted_game = {
                "id": game.id,
                "lobby_id": game.lobby_id,
                "game_status_id": game.game_status_id,
                "creator_id": game.creator_id,
                "player_id": game.player_id,
                "creator_card_id": game.creator_card_id,
                "player_card_id": game.player_card_id,
                "game_type_id": game.game_type_id,
                "opponent_nickname": opponent_nickname,
                "opponent_ready": None,
                "winner_id": game.winner_id
            }

            if game.game_status_id != consts.GameStatus.ACTIVE.value:
                formatted_games.append(formatted_game)
                continue
            if user_is_creator:
                formatted_game["player_card_id"] = None
                formatted_game["opponent_ready"] = bool(game.player_card_id)
            else:
                formatted_game["creator_card_id"] = None
                formatted_game["opponent_ready"] = bool(game.creator_card_id)

            formatted_games.append(formatted_game)

        return formatted_games
