from dataclasses import dataclass

import sqlalchemy as sa

from rockps import entities
from rockps.cases import mixins
from rockps.cases.auth.resetpass.request import base


@dataclass
class UserResetPasswordRequest(
    base.ResetPasswordRequestBase,
    mixins.ValidatePhone,
    mixins.PhonePassConfirmationCode,
):
    sms_service: object
    phone_model: entities.IModel

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
                sa.orm.joinedload(self.phone_model.user),
            )
        )
        confirmed_phone = result.scalars().first()
        await self.validate_object_exists(confirmed_phone)
        await self.validate_phone_is_confirmed(confirmed_phone)
        self.user = confirmed_phone.user
        self.credential = confirmed_phone
