import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio
from sqlalchemy import orm as sa_orm
from sqlalchemy.dialects import postgresql as sa_pgsql

from rockps.adapters.db import mixins


class Sex(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=64),
        nullable=False,
    )


class Phone(
    mixins.Base,
    mixins.BaseIntPrimaryKey,
):
    number = sa.Column(
        sa.String(20),
        nullable=False,
    )

    # Relations
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id'),
        nullable=False,
    )

    user = sa_orm.relationship(
        'User',
        back_populates='phone',
    )


class User(
    mixins.BaseIntPrimaryKey,
    mixins.Password,
    mixins.JWT,
    mixins.Credential,
    mixins.Base,
):
    nickname = sa.Column(
        sa.String(length=128),
        nullable=True,
    )
    password = sa.Column(
        sa_pgsql.BYTEA(),
        nullable=True,
    )
    birth_date = sa.Column(
        sa.Date,
        nullable=True,
    )
    last_session = sa.Column(
        sa.DateTime,
        nullable=True,
    )

    # Relations
    phone_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('phone.id', ondelete='cascade'),
        nullable=False,
    )
    sex_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('sex.id', ondelete='cascade'),
        nullable=False,
    )
    game_lobby_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('game_lobby.id', ondelete='cascade'),
        nullable=True,
    )

    # Reverse relations
    phone = sa_orm.relationship(
        "Phone",
        uselist=False,
        back_populates="user",
    )
    game_lobby = sa_orm.relationship(
        "GameLobby",
        uselist=False,
        back_populates="users"
    )


class GameLobby(
    mixins.Base,
    mixins.BaseIntPrimaryKey,
):
    name = sa.Column(
        sa.String(length=128),
        nullable=False,
    )
    password = sa.Column(
        sa.String(length=128),
        nullable=True,
    )
    is_active = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
    )
    is_public = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
    )

    # Relations
    creator_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=False,
    )

    # Reverse relations
    users = sa_orm.relationship(
        "User",
        back_populates="game_lobby",
    )


class ConfirmationCodeType(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=32),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"ConfirmationCodeType(id={str(self.id)},name={str(self.name)})"


class ConfirmationCode(
    mixins.BaseIntPrimaryKey,
    mixins.Credential,
    mixins.Base
):
    value = sa.Column(
        sa.String(length=4),
        nullable=False,
    )

    # Relations
    call_id = sa.Column(
        sa.String(length=32),
        nullable=True,
    )
    phone_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('phone.id', ondelete='cascade'),
        nullable=True,
    )
    type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('confirmation_code_type.id', ondelete='cascade'),
        nullable=False,
    )

    # Reverse relations
    phone = sa_orm.relationship(
        "Phone",
    )

    async def get_credential(self, session: sa_asyncio.AsyncSession) -> Phone:
        result = await session.execute(
            sa.select(
                Phone
            ).where(
                Phone.id == self.phone_id,
            ).options(
                sa_orm.joinedload(Phone.user),
            )
        )
        return result.scalars().first()

    def __repr__(self) -> str:
        return (
            f"ConfirmationCodeType(id={str(self.id)},"
            f"value={str(self.value)},"
            f"call_id={str(self.call_id)},"
            f"phone_id={str(self.phone_id)},"
            f"type_id={str(self.type_id)})"
        )
