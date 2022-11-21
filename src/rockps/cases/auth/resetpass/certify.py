from dataclasses import dataclass

import sqlalchemy as sa

from rockps import consts
from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class ResetPasswordCertify(
    abstract.CaseDB,
    mixins.ValidateConfirmationCode,
    mixins.ValidatePhone
):
    confirmation_code_model: entities.IModel
    phone_model: entities.IModel
    email_model: entities.IModel
    certificate_model: entities.IModel
    sms_service: object
    data: dict

    def __post_init__(self):
        self.user = None
        self.code = None
        self.credential = None
        self.certificate = None

    async def validate(self):
        await self.validate_code()
        await self.validate_object_exists(self.credential)
        await self.validate_phone_is_confirmed(self.credential)

    async def certify(self):
        self.user = self.credential.user
        self.certificate = self.certificate_model(user=self.user)
        self.session.add(self.certificate)
        # Deletes other confirmation codes for this user
        await self.session.execute(
            sa.delete(
                self.confirmation_code_model
            ).where(
                sa.and_(
                    self.confirmation_code_model.user_id == self.credential.id,
                    self.confirmation_code_model.type_id ==
                        consts.ConfirmationCodeType.RESET
                )
            )
        )
        await self.session.flush()

    async def execute(self, *args, **kwargs) -> dict[str, entities.IModel]:
        await self.validate()
        await self.certify()
        return {
            "user": self.user,
            "certificate": self.certificate,
        }
