from dataclasses import dataclass

import sqlalchemy as sa

from rockps import consts
from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class Confirm(
    abstract.CaseDB,
    mixins.ValidateConfirmationCode,
    mixins.ValidatePhone
):
    confirmation_code_model: entities.IModel
    phone_model: entities.IModel
    sms_service: object
    data: dict

    def __post_init__(self):
        self.code = None
        self.credential = None

    async def validate(self):
        await self.validate_phone_is_not_confirmed(self.credential)
        await self.validate_code()

    async def confirm(self):
        self.credential.is_confirmed = True
        self.session.add(self.credential)
        await self.session.flush()

    async def clear(self):
        await self.session.execute(
            sa.delete(
                self.confirmation_code_model
            ).where(
                sa.and_(
                    self.confirmation_code_model.phone_id == self.credential.id,
                    self.confirmation_code_model.type_id ==
                        consts.ConfirmationCodeType.CONFIRM
                )
            )
        )
        await self.session.flush()

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        await self.confirm()
        await self.clear()
        return self.credential.user
