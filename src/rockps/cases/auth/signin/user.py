from dataclasses import dataclass

import fastapi
import sqlalchemy as sa

from rockps import entities
from rockps import texts
from rockps.cases import mixins
from rockps.cases.auth.signin import base


@dataclass
class UserSignIn(base.BaseSignIn, mixins.ValidatePhone):
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
                sa.orm.joinedload(self.phone_model.user),
            )
        )
        self.phone = result.scalars().first()
        await self.validate_object_exists(self.phone, field="username")
        await self.validate_phone_has_user(self.phone, field="username")

    async def authenticate(self):
        if self.phone.user.is_right_password(self.data["password"]):
            result = await self.session.execute(
                sa.select(
                    self.user_model
                ).where(
                    self.user_model.id == self.phone.user.id
                ).options(
                    sa.orm.joinedload(self.user_model.phone),
                )
            )
            return result.scalars().first()
        raise fastapi.HTTPException(
            detail={
                "loc": ["body", "phone", "password"],
                "msg": texts.WRONG_PHONE_OR_PASSWORD,
                "type": "authorization_error",
            },
            status_code=401,
        )
