from dataclasses import dataclass

import sqlalchemy as sa

from rockps import entities
from rockps.cases import mixins
from rockps.cases.auth.resetpass.request import base


@dataclass
class ClinicResetPasswordRequest(
    base.ResetPasswordRequestBase,
    mixins.ValidateEmail,
    mixins.EmailPassConfirmationCode,
):
    mail_service: object
    email_model: entities.IModel

    async def validate(self):
        result = await self.session.execute(
            sa.select(
                self.email_model
            ).where(
                sa.and_(
                    self.email_model.address == self.data["username"],
                    self.email_model.is_confirmed == True,
                )
            ).options(
                sa.orm.joinedload(self.email_model.clinic)
            )
        )

        confirmed_email = result.scalars().first()
        await self.validate_object_exists(confirmed_email)
        await self.validate_email_is_confirmed(confirmed_email)
        self.user = confirmed_email.clinic
        self.credential = confirmed_email
