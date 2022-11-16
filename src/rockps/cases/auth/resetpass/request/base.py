import abc
from dataclasses import dataclass

from rockps import consts
from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class ResetPasswordRequestBase(
    abstract.CaseDB,
    mixins.BasePassConfirmationCode,
):
    confirmation_code_model: entities.IModel
    data: dict

    def __post_init__(self):
        self.user = None
        self.credential = None

    @abc.abstractmethod
    async def validate(self):
        pass

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        await self.pass_confirmation_code(
            self.credential,
            code_type=consts.ConfirmationCodeType.RESET,
            locale_id=self.data["locale_id"],
        )
        return self.user
