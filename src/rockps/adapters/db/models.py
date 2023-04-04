from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects import postgresql as sa_pgsql

from rockps import consts
from rockps.adapters.db import mixins


class Card(
    mixins.Base,
    mixins.IntPrimaryKey,
):
    name = sa.Column(
        sa.String(length=32),
        nullable=False,
    )


class LobbyStatus(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=32),
        nullable=False,
    )


class LobbyType(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=32),
        nullable=False,
    )


class GameStatus(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=32),
        nullable=False,
    )


class GameType(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=32),
        nullable=False,
    )


class ConfirmationCodeType(
    mixins.IntPrimaryKey,
    mixins.Base,
):
    name = sa.Column(
        sa.String(length=32),
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

    # Relations
    phone_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('phone.id', ondelete='cascade'),
        nullable=False,
    )
    current_lobby_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('lobby.id', ondelete='cascade'),
        nullable=True,
    )

    # Reverse relations
    phone = orm.relationship(
        "models.Phone",
        back_populates="user",
        uselist=False,
        foreign_keys=[phone_id],
    )


class Lobby(
    mixins.Base,
    mixins.BaseIntPrimaryKey,
):
    name = sa.Column(
        sa.String(length=128),
        nullable=False,
    )
    max_games = sa.Column(
        sa.Integer,
        nullable=False,
    )

    # Relations
    creator_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=False,
    )
    player_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=True,
    )
    lobby_status_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('lobby_status.id', ondelete='cascade'),
        server_default=str(consts.LobbyStatus.OPENED.value),
        nullable=False,
    )
    lobby_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('lobby_type.id', ondelete='cascade'),
        nullable=False,
    )


class Game(
    mixins.Base,
    mixins.BaseIntPrimaryKey,
):
    # Relations
    lobby_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('lobby.id', ondelete='cascade'),
        nullable=False,
    )
    creator_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=False,
    )
    player_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='cascade'),
        nullable=True,
    )
    creator_card_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('card.id', ondelete='cascade'),
        nullable=True,
    )
    player_card_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('card.id', ondelete='cascade'),
        nullable=True,
    )
    game_status_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('game_status.id', ondelete='cascade'),
        nullable=False,
        server_default=str(consts.GameStatus.PENDING.value),
    )
    game_type_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('lobby_type.id', ondelete='cascade'),
        nullable=False,
    )

    # Reverse relations
    lobby = orm.relationship(
        "models.Lobby",
        uselist=False,
        foreign_keys=[lobby_id],
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
