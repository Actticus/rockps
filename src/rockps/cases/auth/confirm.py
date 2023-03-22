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
    call_service: object
    data: dict

    def __post_init__(self):
        self.code = None
        self.phone = None

    async def validate(self):
        result = await self.session.execute(
            sa.select(
                self.confirmation_code_model
            ).where(
                self.phone_model.number == self.data["username"]
            ).join(
                self.phone_model,
            ).options(
                sa.orm.joinedload(self.confirmation_code_model.phone),
            ).order_by(
                self.confirmation_code_model.id.desc()
            )
        )
        self.code = result.scalars().first()
        await self.validate_object_exists(self.code)

        await self.validate_phone_is_not_confirmed(self.code.phone)
        await self.validate_code()

    async def confirm(self):
        self.phone.is_confirmed = True
        self.session.add(self.phone)
        await self.session.flush()

    async def clear(self):
        await self.session.execute(
            sa.delete(
                self.confirmation_code_model
            ).where(
                sa.and_(
                    self.confirmation_code_model.phone_id == self.phone.id,
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
        return self.code.user
