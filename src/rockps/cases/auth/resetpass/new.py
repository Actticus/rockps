from dataclasses import dataclass

import sqlalchemy as sa

from rockps import entities
from rockps.cases import abstract
from rockps.cases import mixins


@dataclass
class ResetPasswordNew(
    abstract.CaseDB,
    mixins.ValidateCertificate,
):
    certificate_model: entities.IModel
    data: dict

    def __post_init__(self):
        self.user = None

    async def validate(self):
        certificate = await self.session.get(
            self.certificate_model,
            self.data["certificate"],
            options=[
                sa.orm.joinedload(self.certificate_model.user),
                sa.orm.joinedload(self.certificate_model.clinic),
            ]
        )
        await self.validate_object_exists(certificate)
        self.user = await certificate.get_user()

    async def set_new_password(self):
        self.user.set_password(self.data["new_password"])
        user_model = self.user.__class__
        await self.session.execute(
            sa.update(
                user_model
            ).where(
                user_model.id == self.user.id
            ).values(
                password=self.user.password
            )
        )
        await self.session.flush()

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        await self.set_new_password()
        return self.user
