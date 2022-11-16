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
    mixins.ValidateEmail,
    mixins.ValidatePhone
):
    confirmation_code_model: entities.IModel
    phone_model: entities.IModel
    email_model: entities.IModel
    sms_service: object
    data: dict

    def __post_init__(self):
        self.code = None
        self.credential = None

    async def validate_email(self):
        # TODO: Validate licence is confirmed
        await self.validate_email_is_not_confirmed(self.credential)

    async def validate_phone(self):
        await self.validate_phone_is_not_confirmed(self.credential)

    async def confirm(self):
        self.credential.is_confirmed = True
        self.session.add(self.credential)
        await self.session.flush()

    async def clear(self):
        # TODO: Delete unconfirmed users with the same credentials
        # Hangs up if it is a call auth.
        await self.session.execute(
            sa.delete(
                self.confirmation_code_model
            ).where(
                sa.and_(
                    getattr(
                        self.confirmation_code_model,
                        f"{self.credential.__class__.__name__.lower()}_id",
                    ) == self.credential.id,
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
        return await self.credential.get_user()
