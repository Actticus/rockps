from dataclasses import dataclass

import fastapi
import sqlalchemy as sa
from sqlalchemy import orm

from rockps import entities
from rockps import texts
from rockps.cases import mixins
from rockps.cases.auth import base


@dataclass
class SignIn(base.BaseAuth, mixins.ValidatePhone):
    phone_model: entities.IModel
    user_model: entities.IModel

    def __post_init__(self):
        self.phone = None

    async def validate(self):
        result = await self.session.execute(
            sa.select(
                self.phone_model
            ).where(
                sa.and_(
                    self.phone_model.number == self.data["phone"],
                    self.phone_model.is_confirmed == True,  # pylint: disable=singleton-comparison
                )
            ).options(
                orm.joinedload(self.phone_model.user),
            )
        )
        self.phone = result.scalars().first()
        await self.validate_object_exists(self.phone, field="username")
        await self.validate_phone_has_user(self.phone, field="username")

    async def authenticate(self):
        if self.phone.user.is_right_password(self.data["password"]):
            user = await self.session.get(
                self.user_model,
                self.phone.user.id,
                options=[orm.joinedload(self.user_model.phone)],
            )
            return user
        raise fastapi.HTTPException(
            detail={
                "loc": ["body", "phone", "password"],
                "msg": texts.WRONG_PHONE_OR_PASSWORD,
                "type": "authorization_error",
            },
            status_code=401,
        )

    async def execute(self, *args, **kwargs) -> entities.IModel:
        await self.validate()
        return await self.authenticate()
