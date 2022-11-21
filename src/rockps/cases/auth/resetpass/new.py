from dataclasses import dataclass

from sqlalchemy import orm

from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class ResetPasswordNew(
    abstract.CaseDB,
    mixins.ValidateCertificate,
):
    user_model: entities.IModel
    certificate_model: entities.IModel
    data: dict

    def __post_init__(self):
        self.user = None

    async def validate(self):
        certificate = await self.session.get(
            self.certificate_model,
            self.data["certificate"],
            options=[
                orm.joinedload(self.certificate_model.user),
            ]
        )
        await self.validate_object_exists(certificate)
        self.user = certificate.user

    async def set_new_password(self):
        self.user.set_password(self.data["new_password"])
        self.session.add(self.user)
        await self.session.flush()

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        await self.set_new_password()
        return self.user
