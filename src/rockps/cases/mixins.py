import functools
import random
import string

import fastapi
import sqlalchemy as sa
from fastapi import status
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession

from rockps import entities
from rockps import texts


# TODO: Refactor it in favor of using class-level field in base class.
def _set_field_default(func):
    """Sets default value for field param if it missing.

    Firstly, tries to get default field value from class attribute and then,
    if class attribute also missing, just derive field value from object's
    class name.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):

        def safe_get_from(args, idx):
            try:
                return args[idx]
            except IndexError:
                return None

        cls = args[0]
        kwargs = {
            "obj": safe_get_from(args, idx=1),
            "field": safe_get_from(args, idx=2),
            **kwargs,
        }
        if not kwargs["field"]:
            cls_field = getattr(cls, "field", None)
            obj_field = kwargs["obj"].__class__.__name__.lower()
            kwargs["field"] = cls_field or obj_field
        return await func(cls, **kwargs)

    return wrapper


class BaseValidate:

    @classmethod
    def raise_validation_error(
        cls,
        message,
        field,
        code: int | None = status.HTTP_422_UNPROCESSABLE_ENTITY
    ):
        # TODO: refactor old mixins
        raise fastapi.HTTPException(
            status_code=code,
            detail=[{
                "loc": ["body", field],
                "msg": message,
                "type": "validation_error",
            }]
        )

    @classmethod
    def raise_validation_error_refactored(
        cls,
        detail: dict | list,
        code: int | None = status.HTTP_422_UNPROCESSABLE_ENTITY,
    ):
        raise fastapi.HTTPException(
            status_code=code,
            detail=detail,
        )


class ValidateObject(BaseValidate):

    @classmethod
    @_set_field_default
    async def validate_object_exists(
        cls,
        obj,
        field: str | None = None,
        code: int | None = status.HTTP_422_UNPROCESSABLE_ENTITY,
        message: str | None = texts.DOES_NOT_EXISTS,
    ):
        if not obj:
            cls.raise_validation_error(message, field, code)

    @classmethod
    @_set_field_default
    async def validate_object_does_not_exists(
        cls,
        obj,
        field: str | None = None,
        code: int | None = status.HTTP_422_UNPROCESSABLE_ENTITY
    ):
        if obj:
            cls.raise_validation_error(texts.ALREADY_EXISTS, field, code)


class ValidatePhone(ValidateObject):
    field = "phone"

    @classmethod
    async def validate_phone_is_not_confirmed(
        cls,
        phone,
        field: str | None = None,
    ):
        if phone.is_confirmed:
            cls.raise_validation_error(texts.ALREADY_CONFIRMED, field)

    @classmethod
    async def validate_phone_is_confirmed(
        cls,
        phone,
        field: str | None = None,
    ):
        if not phone.is_confirmed:
            cls.raise_validation_error(texts.NOT_CONFIRMED, field)

    @classmethod
    async def validate_phone_has_user(
        cls,
        phone,
        field: str | None = None,
    ):
        if not phone.user:
            cls.raise_validation_error(texts.PHONE_USER_DOES_NOT_EXIST, field)


class ValidateCertificate(ValidateObject):
    field = "certificate"


class PassConfirmationCode:
    session: AsyncSession
    confirmation_code_model: entities.IModel
    call_service: object

    async def pass_confirmation_code(self, phone, code_type):
        code = self.confirmation_code_model(
            value=''.join(random.choice(string.digits) for _ in range(4)),
            phone=phone,
            type_id=code_type,
        )
        code.call_id = await self.call_service.call(phone.number, code.value)
        self.session.add(code)
        await self.session.flush()


class ValidateConfirmationCode(ValidateObject):
    session: AsyncSession
    confirmation_code_model: entities.IModel
    phone_model: entities.IModel
    code: object
    phone: object

    async def validate_code(self):
        result = await self.session.execute(
            sa.select(
                self.confirmation_code_model
            ).where(
                self.phone_model.number == self.data["username"]
            ).join(
                self.phone_model,
            ).options(
                orm.joinedload(
                    self.confirmation_code_model.phone,
                ).joinedload(
                    self.phone_model.user,
                ),
            ).order_by(
                self.confirmation_code_model.id.desc()
            )
        )
        self.code = result.scalars().first()
        await self.validate_object_exists(self.code)

        self.phone = self.code.phone
        await self.validate_object_exists(self.code.value == self.data["code"])
