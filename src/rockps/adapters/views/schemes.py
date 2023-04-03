from __future__ import annotations

import uuid
from typing import Generic
from typing import TypeVar

import pydantic
from pydantic import validator

from rockps import consts
from rockps import texts


class Base(pydantic.BaseModel):  # pylint: disable=no-member
    class Config:
        orm_mode = True
        extra = 'ignore'

    @classmethod
    def properties_names(cls) -> list[str]:
        return list(cls.__fields__.keys())


class Identifier(Base):
    id: int


class GamePatch(Base):
    id: int
    card_id: consts.Card


class GameGet(Base):
    id: int
    lobby_id: int
    creator_id: int
    player_id: int
    creator_card_id: consts.Card
    player_card_id: consts.Card
    game_status_id: consts.GameStatus
    opponent_ready: bool


class LobbyPatch(Base):
    id: int | None
    lobby_action_id: consts.LobbyAction


class LobbyPost(Base):
    name: str = pydantic.Field(min_length=5, max_length=32)
    max_games: int = pydantic.Field(ge=1, le=5)
    lobby_type_id: consts.LobbyType

    @validator("max_games")
    @classmethod
    def max_games_must_be_odd(cls, value):
        if value % 2 == 0:
            raise ValueError(texts.MAX_GAMES_MUST_BE_ODD)
        return value


class ConfirmationCode(Base):
    username: str = pydantic.Field()
    code: str = pydantic.Field()


class UserGet(Base):
    id: int
    nickname: str = pydantic.Field(min_length=2, max_length=128)


class LobbyGet(Base):
    id: int
    name: str
    max_games: int
    lobby_type_id: consts.LobbyType


class SuccessSignIn(Base):
    user: UserGet
    access_token: str
    token_type: str


class UserSignUp(Base):
    phone: str = pydantic.Field(min_length=12, max_length=16)
    password: str = pydantic.Field(min_length=8, max_length=64)
    nickname: str = pydantic.Field(min_length=2, max_length=128)

    @validator("phone")
    @classmethod
    def phone_must_contain_plus(cls, value):
        if "+" in value:
            return value
        # TODO: Make validation more precise
        raise ValueError(texts.NOT_VALID_PHONE)


class NewPassword(Base):
    certificate: uuid.UUID
    new_password: str = pydantic.Field(min_length=8, max_length=64)


class ResetPasswordRequest(Base):
    username: str = pydantic.Field(min_length=1, max_length=256)

    @validator("username")
    @classmethod
    def username_must_contain_plus(cls, value):
        if "+" in value:
            return value
        # TODO: Make validation more precise
        raise ValueError(texts.NOT_VALID_PHONE)


_PAGE_ITEM = TypeVar('_PAGE_ITEM')


class Page(Base, Generic[_PAGE_ITEM]):
    items: list[_PAGE_ITEM]
    total: int
    size: int
