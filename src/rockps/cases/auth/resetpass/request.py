from dataclasses import dataclass

import sqlalchemy as sa
from sqlalchemy import orm

from rockps import consts
from rockps import entities
from rockps.cases import mixins
from rockps.cases.auth import base


@dataclass
class ResetPasswordRequest(
    base.BaseAuth,
    mixins.ValidatePhone,
    mixins.PassConfirmationCode,
):
    call_service: object
    phone_model: entities.IModel
    confirmation_code_model: entities.IModel

    def __post_init__(self):
        self.user = None
        self.phone = None

    async def validate(self):
        result = await self.session.execute(
            sa.select(
                self.phone_model
            ).where(
                sa.and_(
                    self.phone_model.number == self.data["username"],
                    self.phone_model.is_confirmed == True,  # pylint: disable=singleton-comparison
                )
            ).options(
                orm.joinedload(self.phone_model.user),
            )
        )
        confirmed_phone = result.scalars().first()
        await self.validate_object_exists(confirmed_phone)
        await self.validate_phone_is_confirmed(confirmed_phone)
        self.user = confirmed_phone.user
        self.phone = confirmed_phone

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        await self.pass_confirmation_code(
            self.phone,
            code_type=consts.ConfirmationCodeType.RESET,
        )
        return self.user
