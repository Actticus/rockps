"""This module contains general for whole API version schemes."""
import datetime
import uuid

import pydantic
from pydantic import validator

from rockps import consts


class Base(pydantic.BaseModel):  # pylint: disable=no-member
    class Config:
        orm_mode = True
        extra = 'forbid'

    @classmethod
    def properties_names(cls) -> list[str]:
        return list(cls.__fields__.keys())


class Identifier(Base):
    id: int


class ConfirmationCode(Base):
    code: str = pydantic.Field()


class UserUpdate(Base):
    id: int
    first_name: str | None = pydantic.Field(min_length=2, max_length=128)
    middle_name: str | None = pydantic.Field(min_length=0, max_length=128)
    last_name: str | None = pydantic.Field(min_length=2, max_length=128)
    birth_date: datetime.date | None
    sex_id: consts.Sex | None
    last_session: datetime.datetime | None


class UserCreate(Base):
    phone: str | None = pydantic.Field(min_length=12, max_length=16)
    first_name: str = pydantic.Field(min_length=2, max_length=128)
    middle_name: str | None = pydantic.Field(min_length=2, max_length=128)
    last_name: str = pydantic.Field(min_length=2, max_length=128)
    birth_date: datetime.date
    diagnosis_ids: list[consts.Diagnosis]
    sex_id: consts.Sex
    last_session: datetime.datetime | None


class User(Base):
    id: int
    created_dt: datetime.datetime
    first_name: str = pydantic.Field(min_length=2, max_length=128)
    middle_name: str | None = pydantic.Field(min_length=0, max_length=128)
    last_name: str = pydantic.Field(min_length=2, max_length=128)
    sex_id: consts.Sex
    birth_date: datetime.date
    last_session: datetime.datetime | None
    phone: str | None
    diagnosis_id: consts.Diagnosis
    archive_status_id: consts.ArchiveStatus
    version: int

    @validator('phone', pre=True)
    @classmethod
    def phone_to_str(cls, phone):
        return str(phone) if phone else None


class SuccessSignIn(Base):
    user: User
    access_token: str
    token_type: str


class UserSignUp(Base):
    phone: str = pydantic.Field(min_length=12, max_length=16)
    password: str = pydantic.Field(min_length=8, max_length=64)
    first_name: str = pydantic.Field(min_length=2, max_length=128)
    middle_name: str | None = pydantic.Field(min_length=2, max_length=128)
    last_name: str = pydantic.Field(min_length=2, max_length=128)
    birth_date: datetime.date
    sex_id: consts.Sex


class NewPassword(Base):
    certificate: uuid.UUID
    new_password: str = pydantic.Field(min_length=8, max_length=64)


class ResetPasswordRequest(Base):
    username: str = pydantic.Field(min_length=1, max_length=256)
    locale_id: consts.Locale = pydantic.Field(consts.Locale.EN)

    @validator("username")
    @classmethod
    def username_must_contain_plus(cls, value):
        if "+" in value:
            return value
        # TODO: Make validation more precise
        raise ValueError("it is not valid phone")
