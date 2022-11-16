import abc
import functools
import random
import string

import fastapi
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio
from fastapi import status

from rockps import consts
from rockps import entities
from rockps import texts
from rockps.adapters import models


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
            detail={
                "loc": ["body", field],
                "msg": message,
                "type": "validation_error",
            }
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


class ValidateEmail(ValidateObject):
    field = "email"

    @classmethod
    async def validate_email_is_not_confirmed(
        cls,
        email,
        field: str | None = None,
    ):
        if email.is_confirmed:
            cls.raise_validation_error(texts.ALREADY_CONFIRMED, field)

    @classmethod
    async def validate_email_is_confirmed(
        cls,
        email,
        field: str | None = None,
    ):
        if not email.is_confirmed:
            cls.raise_validation_error(texts.NOT_CONFIRMED, field)

    @classmethod
    async def validate_email_has_user(
        cls,
        email,
        field: str | None = None,
    ):
        if not await email.get_user():
            cls.raise_validation_error(texts.EMAIL_USER_DOES_NOT_EXIST, field)


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
        if not await phone.get_user():
            cls.raise_validation_error(texts.PHONE_USER_DOES_NOT_EXIST, field)


class ValidatePhones(BaseValidate):

    @classmethod
    async def validate_phones_are_not_confirmed(
        cls,
        session,
        patient_phones,
    ):
        result = await session.execute(
            sa.select(
                models.Phone.number
            ).where(
                sa.and_(
                    models.Phone.number.in_(
                        patient_phones
                    ),
                    models.Phone.is_confirmed == True,  # pylint: disable=singleton-comparison
                )
            ).execution_options(
                populate_existing=True,
            )
        )
        if not (confirmed_phones := result.scalars().all()):
            return

        detail = []
        for confirmed_phone in confirmed_phones:
            detail.append({
                "loc": [
                    "body",
                    patient_phones.index(confirmed_phone),
                    "phone"
                ],
                "msg": texts.ALREADY_EXISTS,
                "type": "validation_error.phone"
            })
        await cls.raise_validation_error_refactored(detail)


class ValidateConfirmationCode(ValidateObject):
    field = "code"

    @abc.abstractmethod
    async def validate_email(self):
        pass

    @abc.abstractmethod
    async def validate_phone(self):
        pass

    async def validate(self):
        # pylint: disable=attribute-defined-outside-init,disable=no-member
        if "@" in self.data["username"]:
            result = await self.session.execute(
                sa.select(
                    self.confirmation_code_model
                ).where(
                    self.email_model.address == self.data["username"]
                ).join(
                    self.email_model,
                ).options(
                    sa.orm.joinedload(self.confirmation_code_model.phone),
                    sa.orm.joinedload(self.confirmation_code_model.email),
                ).order_by(
                    self.confirmation_code_model.id.desc()
                )
            )
        else:
            result = await self.session.execute(
                sa.select(
                    self.confirmation_code_model
                ).where(
                    self.phone_model.number == self.data["username"]
                ).join(
                    self.phone_model,
                ).options(
                    sa.orm.joinedload(self.confirmation_code_model.phone),
                    sa.orm.joinedload(self.confirmation_code_model.email),
                ).order_by(
                    self.confirmation_code_model.id.desc()
                )
            )
        self.code = result.scalars().first()
        await self.validate_object_exists(self.code)

        self.credential = await self.code.get_credential(self.session)
        if self.credential.get_type_name() == "phone":
            valid = await self.sms_service.check(
                self.credential.number,
                self.data["code"],
            )
            await self.validate_object_exists(valid)
            await self.validate_phone()
        elif self.credential.get_type_name() == "email":
            await self.validate_object_exists(
                self.code.value == self.data["code"],
            )
            await self.validate_email()
        else:
            raise Exception("WTF?")  # pragma: nocover


class ValidateCertificate(ValidateObject):
    field = "certificate"


class BasePassConfirmationCode(abc.ABC):

    @abc.abstractmethod
    async def pass_confirmation_code(self, credential, code_type, locale_id):
        pass


class PhonePassConfirmationCode(BasePassConfirmationCode):

    # TODO: Validate unique constraint
    async def pass_confirmation_code(self, phone, code_type, locale_id):  # pylint: disable=arguments-renamed
        # pylint: disable=no-member
        code = self.confirmation_code_model(
            value=''.join(random.choice(string.digits) for _ in range(4)),
            phone=phone,
            type_id=code_type,
        )
        code.call_id = await self.sms_service.sms(number=phone.number)
        self.session.add(code)
        await self.session.flush()


class EmailPassConfirmationCode(BasePassConfirmationCode):

    # TODO: Validate unique constraint
    async def pass_confirmation_code(self, email, code_type, locale_id):  # pylint: disable=arguments-renamed
        code = self.confirmation_code_model(
            value=''.join(random.choice(string.digits) for _ in range(4)),
            email_id=email.id,
            type_id=code_type,
        )
        self.session.add(code)
        await self.session.flush()
        await self.session.refresh(code)
        if code_type == consts.ConfirmationCodeType.CONFIRM:
            func = self.mail_service.send_confirmation_code
        elif code_type == consts.ConfirmationCodeType.RESET:
            func = self.mail_service.send_reset_code
        await func(
            address=email.address,
            code=code.value,
            locale_id=locale_id,
        )


class DbState:
    session: sa_asyncio.AsyncSession
    model: entities.IModel

    async def get_current_db_state(self, ids, join=None):
        request = sa.select(
            self.model
        ).where(
            self.model.id.in_(ids)
        ).order_by(
            self.model.id
        ).execution_options(
            populate_existing=True,
        )
        if join:
            request = request.options(join)

        result = await self.session.execute(request)
        return result.scalars().all()
