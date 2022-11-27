from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import orm
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

    def __repr__(self) -> str:
        return (
            f"<Sex("
            f"id={self.id}, "
            f"name={self.name}"
            f")>"
        )


class Phone(
    mixins.Base,
    mixins.BaseIntPrimaryKey,
):
    number = sa.Column(
        sa.String(20),
        nullable=False,
    )
    is_confirmed = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
    )

    # Reverse relations
    user = orm.relationship(
        'models.User',
        uselist=False,
        back_populates='phone',
    )

    def __str__(self) -> str:
        return str(self.number)

    __table_args__ = (
        sa.Index(
            'uniq_confirmed_number_idx',
            number,
            unique=True,
            postgresql_where=is_confirmed,
        ),
    )


class User(
    mixins.BaseIntPrimaryKey,
    mixins.Password,
    mixins.JWT,
    mixins.Base,
):
    nickname = sa.Column(
        sa.String(length=128),
        nullable=True,
    )
    password = sa.Column(
        sa_pgsql.BYTEA(),
        nullable=False,
    )
    birth_date = sa.Column(
        sa.Date,
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
    lobby_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('lobby.id', ondelete='cascade'),
        nullable=True,
    )

    # Reverse relations
    phone = orm.relationship(
        "models.Phone",
        back_populates="user",
        uselist=False,
        lazy="noload",
        foreign_keys=[phone_id],
    )
    lobby = orm.relationship(
        "models.Lobby",
        uselist=False,
        back_populates="users",
        foreign_keys=[lobby_id],
    )

    def __repr__(self):
        return (
            f"<User("
            f"id={self.id}, "
            f"nickname={self.nickname}, "
            f"birth_date={self.birth_date}, "
            f"phone_id={self.phone_id}, "
            f"sex_id={self.sex_id}, "
            f"lobby_id={self.lobby_id}"
            f")>"
        )


class Lobby(
    mixins.Base,
    mixins.BaseIntPrimaryKey,
    mixins.Password,
):
    name = sa.Column(
        sa.String(length=128),
        nullable=False,
    )
    password = sa.Column(
        sa_pgsql.BYTEA(),
        nullable=True,
    )
    is_public = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
    )
    max_players = sa.Column(
        sa.Integer,
        nullable=False,
        default=2,
    )

    # Relations
    creator_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=False,
    )

    # Reverse relations
    users = orm.relationship(
        "models.User",
        back_populates="lobby",
        foreign_keys=[User.lobby_id],
    )

    def __repr__(self):
        return (
            f"<Lobby("
            f"id={self.id}, "
            f"name={self.name}, "
            f"password={self.password}, "
            f"is_public={self.is_public}, "
            f"max_players={self.max_players}, "
            f"creator_id={self.creator_id}"
            f")>"
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
        return (
            f"<ConfirmationCodeType("
            f"id={self.id}, "
            f"name={self.name}"
            f")>"
        )


class ConfirmationCode(
    mixins.BaseIntPrimaryKey,
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
    phone = orm.relationship(
        "models.Phone",
        uselist=False,
        foreign_keys=[phone_id],
    )

    def __repr__(self) -> str:
        return (
            f"<ConfirmationCodeType("
            f"id={str(self.id)}, "
            f"value={str(self.value)}, "
            f"call_id={str(self.call_id)}, "
            f"phone_id={str(self.phone_id)}, "
            f"type_id={str(self.type_id)}"
            f")>"
        )


class Certificate(
    mixins.BaseUUIDPrimaryKey,
    mixins.Base,
):
    # Relations
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=True,
    )

    # Reverse relations
    user = orm.relationship(
        "models.User",
        uselist=False,
        foreign_keys=[user_id],
    )
