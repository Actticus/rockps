import fastapi
import jose
import sqlalchemy.ext.asyncio as sa_asyncio
from fastapi import security
from jose import jwt

from backend import settings
from backend import texts
from backend.adapters import models
from backend.adapters import sessions

OAUTH2_SCHEME = security.OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign_in")


async def get_user(
    token: str = fastapi.Depends(OAUTH2_SCHEME),
    session: sa_asyncio.AsyncSession = fastapi.Depends(
        sessions.create_session
    ),
):
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail=texts.COULD_NOT_VALIDATE_CREDITS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jose.JWTError:
        raise credentials_exception  # pylint: disable=raise-missing-from
    if (user_id := payload.get("sub")) is None:
        raise credentials_exception
    if not user_id.isdigit():
        raise credentials_exception
    model = getattr(models, payload.get("type").capitalize())
    if (user := await session.get(model, int(user_id))) is None:
        raise credentials_exception
    return user


async def get_confirmed_user(
    user: models.Clinic | models.Patient = fastapi.Depends(get_user),
    session: sa_asyncio.AsyncSession = fastapi.Depends(
        sessions.create_session
    ),
):
    if not await user.check_credential_confirmed(session):
        raise fastapi.HTTPException(
            status_code=400,
            detail=texts.UNCONFIRMED_USER,
        )
    return user


async def get_confirmed_clinic(
    user: models.Clinic | models.Patient = fastapi.Depends(
        get_confirmed_user
    )
):
    if not user.is_clinic:
        raise fastapi.HTTPException(
            status_code=403,
            detail=texts.FORBIDDEN_FOR_PATIENT,
        )
    return user


async def validate_allowed_to_patient(
    requesting_user,
    patient_id,
    loc,
    patient_msg,
    clinic_msg,
    session
):
    field = loc[1]

    # A patient has access only to himself.
    if (requesting_user.is_patient and requesting_user.id != patient_id):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "loc": loc,
                "msg": patient_msg,
                "type": f"validation_error.{field}",
            },
        )

    # A clinic has access only to its patients.
    if (requesting_user.is_clinic and
            not await requesting_user.check_has_patient(patient_id, session)):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "loc": loc,
                "msg": clinic_msg,
                "type": f"validation_error.{field}",
            },
        )


async def validate_allowed_to_patients(
    requesting_user,
    patient_ids,
    loc,
    patient_msg,
    clinic_msg,
    session
):
    field = loc[1]
    # A patient has access only to himself.
    if (
        requesting_user.is_patient and
            all(
                requesting_user.id != patient_id
                for patient_id in patient_ids
            )
    ):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{
                "loc": [loc[0], 0, loc[1]],
                "msg": patient_msg,
                "type": f"validation_error.{field}",
            }],
        )

    # A clinic has access only to its patients.
    if requesting_user.is_clinic:
        clinic_ids = await models.Patient.get_clinic_ids(patient_ids, session)
        detail = []
        for i, clinic_id in enumerate(clinic_ids):
            if clinic_id != requesting_user.id:
                detail.append({
                    "loc": [loc[0], i, loc[1]],
                    "msg": clinic_msg,
                    "type": f"validation_error.{field}",
                })
        if detail:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=detail,
            )


async def validate_allowed_to_measurements(
    requesting_user,
    measurements_ids,
    loc,
    patient_msg,
    clinic_msg,
    session
):
    field = loc[1]
    if requesting_user.is_patient:
        get_user_ids = models.Measurement.get_patient_ids
        msg = patient_msg
    else:
        get_user_ids = models.Measurement.get_clinic_ids
        msg = clinic_msg

    user_ids = await get_user_ids(
        measurements_ids,
        session,
    )
    detail = []
    for i, user_id in enumerate(user_ids):
        if user_id != requesting_user.id:
            detail.append({
                "loc": [loc[0], i, loc[1]],
                "msg": msg,
                "type": f"validation_error.{field}",
            })

    if detail:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


async def validate_allowed_to_game_result(
    requesting_user,
    game_result_id,
    loc,
    patient_msg,
    clinic_msg,
    session
):
    field = loc[1]
    if requesting_user.is_patient:
        get_user_ids = models.GameResult.get_patient_ids
        msg = patient_msg
    else:
        get_user_ids = models.GameResult.get_clinic_ids
        msg = clinic_msg

    user_id = await get_user_ids(
        [game_result_id],
        session,
    )

    detail = []
    if not user_id:
        detail = [{
            "loc": ["body", loc[1]],
            "msg": msg,
            "type": f"validation_error.{field}",
        }]

    if user_id[0] != requesting_user.id:
        detail = [{
            "loc": ["body", loc[1]],
            "msg": msg,
            "type": f"validation_error.{field}",
        }]

    if detail:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


async def validate_allowed_to_game_results(
    requesting_user,
    game_results_ids,
    loc,
    patient_msg,
    clinic_msg,
    session
):
    field = loc[1]
    if requesting_user.is_patient:
        get_user_ids = models.GameResult.get_patient_ids
        msg = patient_msg
    else:
        get_user_ids = models.GameResult.get_clinic_ids
        msg = clinic_msg

    user_ids = await get_user_ids(
        game_results_ids,
        session,
    )
    detail = []
    for i, user_id in enumerate(user_ids):
        if user_id != requesting_user.id:
            detail.append({
                "loc": [loc[0], i, loc[1]],
                "msg": msg,
                "type": f"validation_error.{field}",
            })

    if detail:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


async def validate_allowed_to_goals(
    requesting_user,
    goals_ids,
    loc,
    patient_msg,
    clinic_msg,
    session
):
    field = loc[1]
    if requesting_user.is_patient:
        get_user_ids = models.Goal.get_patient_ids
        msg = patient_msg
    else:
        get_user_ids = models.Goal.get_clinic_ids
        msg = clinic_msg

    user_ids = await get_user_ids(
        goals_ids,
        session,
    )
    detail = []
    for i, user_id in enumerate(user_ids):
        if user_id != requesting_user.id:
            detail.append({
                "loc": [loc[0], i, loc[1]],
                "msg": msg,
                "type": f"validation_error.{field}",
            })

    if detail:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
