import datetime
import re
from uuid import uuid4

import bcrypt
import sqlalchemy as sa
from jose import jwt
from sqlalchemy.dialects import postgresql as sa_pgsql
from sqlalchemy.ext import declarative as sa_declarative

from rockps import settings


class AutoTableName:

    @sa_declarative.declared_attr
    def __tablename__(cls):  # pylint: disable=no-self-argument
        return '_'.join(re.findall('[A-Z][^A-Z]*', cls.__name__)).lower()


Base = sa_declarative.declarative_base(cls=AutoTableName)


class Password:

    def set_password(self, password: str):
        self.password = bcrypt.hashpw(  # pylint: disable=attribute-defined-outside-init
            password=bytes(password, "ascii"),
            salt=bcrypt.gensalt(),
        )

    def is_right_password(self, password: str):
        return bcrypt.checkpw(
            password=bytes(password, "ascii"),
            hashed_password=self.password,
        )


class JWT:

    def create_access_token(self):
        expires_delta = datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        expire = datetime.datetime.utcnow() + expires_delta
        return jwt.encode(
            {
                "sub": str(self.id),
                "exp": expire,
            },
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )


class CreatedDTFrontend:
    created_dt_frontend = sa.Column(
        sa.DateTime,
        nullable=False,
    )


class UUIDPrimaryKey:
    id = sa.Column(
        sa_pgsql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
    )


class TypeName:

    @classmethod
    def get_type_name(cls) -> str:
        return cls.__name__.lower()


class IntPrimaryKey:
    id = sa.Column(
        sa.Integer,
        primary_key=True,
        nullable=False,
    )


class CreatedDT:
    created_dt = sa.Column(
        sa.DateTime,
        server_default=sa.text('NOW()'),
        nullable=False,
    )


class BaseIntPrimaryKey(
    IntPrimaryKey,
    CreatedDT
):
    pass


class BaseUUIDPrimaryKey(
    UUIDPrimaryKey,
    CreatedDT
):
    pass
