import abc
from dataclasses import dataclass

from rockps import consts
from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class BaseSignUp(abstract.CaseDB, mixins.BasePassConfirmationCode):
    confirmation_code_model: entities.IModel
    data: dict

    def __post_init__(self):
        self.credential = None

    @abc.abstractmethod
    async def validate(self):
        pass

    @abc.abstractmethod
    async def create_user(self):
        pass

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        user = await self.create_user()
        await self.pass_confirmation_code(
            self.credential,
            code_type=consts.ConfirmationCodeType.CONFIRM,
            locale_id=self.data["locale_id"],
        )
        return user
