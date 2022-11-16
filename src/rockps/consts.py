import enum


class DictMixin:

    @classmethod
    def values(cls):
        return tuple(i.value for i in cls)  # pragma: nocover

    @classmethod
    def keys(cls):
        return tuple(i.name for i in cls)  # pragma: nocover

    @classmethod
    def items(cls):
        return list((i.name, i.value) for i in cls)  # pragma: nocover


@enum.unique
class Sex(DictMixin, enum.IntEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3


@enum.unique
class ConfirmationCodeType(DictMixin, enum.IntEnum):
    CONFIRM = 1
    RESET = 2
