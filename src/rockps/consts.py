import enum


class DictMixin:

    @classmethod
    def values(cls):
        return tuple(i.value for i in cls)

    @classmethod
    def keys(cls):
        return tuple(i.name for i in cls)

    @classmethod
    def items(cls):
        return list((i.name, i.value) for i in cls)


@enum.unique
class ConfirmationCodeType(DictMixin, enum.IntEnum):
    CONFIRM = 1
    RESET = 2


@enum.unique
class Card(DictMixin, enum.IntEnum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3
    LIZARD = 4
    SPOCK = 5


@enum.unique
class LobbyStatus(DictMixin, enum.IntEnum):
    OPENED = 1
    ACTIVE = 2
    FINISHED = 3
    CANCELED = 4


@enum.unique
class LobbyType(DictMixin, enum.IntEnum):
    STANDARD = 1
    EXTENDED = 2


class LobbyAction(DictMixin, enum.IntEnum):
    JOIN = 1
    LEAVE = 2


@enum.unique
class GameStatus(DictMixin, enum.IntEnum):
    PENDING = 1
    ACTIVE = 2
    FINISHED = 3
    CANCELED = 4


@enum.unique
class GameType(DictMixin, enum.IntEnum):
    STANDARD = 1
    EXTENDED = 2
