from dataclasses import dataclass

import sqlalchemy as sa

from rockps import consts
from rockps import entities
from rockps.cases import mixins
from rockps.cases.auth import base


@dataclass
class SignUp(
    base.BaseAuth,
    mixins.ValidatePhone,
    mixins.PassConfirmationCode
):
    confirmation_code_model: entities.IModel
    sms_service: object
    phone_model: entities.IModel
    user_model: entities.IModel

    def __post_init__(self):
        self.credential = None

    async def validate(self):
        result = await self.session.execute(
            sa.select(
                self.phone_model
            ).where(
                sa.and_(
                    self.phone_model.number == self.data["phone"],
                    self.phone_model.is_confirmed == True,  # pylint: disable=singleton-comparison
                )
            )
        )
        confirmed_phone = result.scalars().first()
        await self.validate_object_does_not_exists(confirmed_phone)

    async def create_user(self):
        password = self.data.pop("password")
        self.data["phone"] = self.phone_model(number=self.data["phone"])
        user = self.user_model(**self.data)
        user.set_password(password)
        self.data["phone"].user = user
        self.credential = self.data["phone"]

        self.session.add(self.data["phone"])
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        user = await self.create_user()
        await self.pass_confirmation_code(
            self.credential,
            code_type=consts.ConfirmationCodeType.CONFIRM,
        )
        return user
