from __future__ import annotations

import datetime
import uuid
from typing import Generic
from typing import TypeVar

import pydantic
from pydantic import root_validator
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


class LobbyPost(Base):
    name: str = pydantic.Field(min_length=5, max_length=32)
    is_public: bool = True
    password: str = pydantic.Field(None, min_length=4, max_length=16)
    max_players: int = pydantic.Field(2, ge=2, le=16)

    @root_validator
    @classmethod
    def public_lobby_password(cls, values: dict) -> dict:
        is_public = values.get('is_public')
        password = values.get('password')
        if not is_public and not password:
            raise ValueError(texts.NOT_PUBLIC_LOBBY_MUST_HAVE_PASSWORD)
        if is_public and password:
            raise ValueError(texts.PUBLIC_LOBBY_MUST_NOT_HAVE_PASSWORD)
        return values


class ConfirmationCode(Base):
    username: str = pydantic.Field()
    code: str = pydantic.Field()


class UserUpdate(Base):
    id: int
    first_name: str | None = pydantic.Field(min_length=2, max_length=128)
    middle_name: str | None = pydantic.Field(min_length=0, max_length=128)
    last_name: str | None = pydantic.Field(min_length=2, max_length=128)
    birth_date: datetime.date | None
    sex_id: consts.Sex | None
    last_session: datetime.datetime | None


class UserGet(Base):
    id: int
    created_dt: datetime.datetime
    nickname: str = pydantic.Field(min_length=2, max_length=128)
    sex_id: consts.Sex
    birth_date: datetime.date
    phone: str | None
    lobby: LobbyGet | None

    @validator('phone', pre=True)
    @classmethod
    def phone_to_str(cls, phone):
        return str(phone) if phone else None


class LobbyGet(Base):
    id: int
    name: str
    is_public: bool
    max_players: int
    users: list[UserGet]


class SuccessSignIn(Base):
    user: UserGet
    access_token: str
    token_type: str


class UserSignUp(Base):
    phone: str = pydantic.Field(min_length=12, max_length=16)
    password: str = pydantic.Field(min_length=8, max_length=64)
    nickname: str = pydantic.Field(min_length=2, max_length=128)
    birth_date: datetime.date
    sex_id: consts.Sex


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


def update_forward_refs() -> None:
    UserGet.update_forward_refs()
