import fastapi
import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps import cases
from rockps import texts
from rockps.adapters import models
from rockps.adapters import sessions
from rockps.adapters.views import schemes
from rockps.adapters.views.v1 import access


class Lobby:
    router = fastapi.APIRouter()

    @staticmethod
    @router.post("/create", response_model=schemes.Identifier)
    async def post(
        lobby_data: schemes.LobbyCreate,
        requesting_user: models.User = fastapi.Depends(
            access.get_confirmed_user,
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        if requesting_user.lobby_id:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail=texts.USER_ALREADY_IN_LOBBY,
            )

        case = cases.CreateLobby(
            model=models.Lobby,
            data={
                "creator_id": requesting_user.id,
                **lobby_data,
            },
            session=session,
        )
        patient = await case.execute()
        return {"id": patient.id}

    @staticmethod
    @router.post("/", response_model=schemes.Identifier, status_code=201)
    async def post(
        creating_patient: schemes.PatientCreate,
        requesting_patient: schemes.User = fastapi.Depends(
            access.get_confirmed_clinic
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        data = creating_patient.dict(exclude_none=True)
        # FIXME: Bug on frontend, already fixed in master
        # Will be deleted, when all users will be updated
        if "last_session" in data:
            if data["last_session"].tzinfo is not None:
                # pylint: disable=line-too-long
                logger.info("!!!TZINFO IS NOT NONE!!!")  # pragma: nocover
                data["last_session"] = data["last_session"].replace(tzinfo=None)  # pragma: nocover
        if "diagnosis_ids" in data:
            data["diagnosis_id"] = data.pop("diagnosis_ids")[0]

        case = cases.CreatePatient(
            model=models.Patient,
            phone_model=models.Phone,
            diagnosis_model=models.Diagnosis,
            data={
                "clinic": requesting_patient,
                **data,
            },
            session=session
        )
        patient = await case.execute()
        return {"id": patient.id}

    @staticmethod
    @router.get("/", response_model=list[schemes.Patient])
    async def get(
        start_with_id: int | None = 0,
        requesting_clinic: schemes.User = fastapi.Depends(
            access.get_confirmed_clinic
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        result = await session.execute(
            sa.select(
                models.Patient
            ).where(
                sa.and_(
                    models.Patient.id >= start_with_id,
                    models.Patient.clinic_id == requesting_clinic.id,
                )
            ).order_by(
                models.Patient.id
            ).options(
                sa.orm.joinedload(models.Patient.clinic),
                sa.orm.joinedload(models.Patient.phone),
                sa.orm.joinedload(models.Patient.diagnosis),
                sa.orm.joinedload(models.Patient.sex),
            )
        )
        patients = result.unique().scalars().all()
        return [schemes.Patient.from_orm(patient) for patient in patients]

    @staticmethod
    @router.get("/{patient_id}", response_model=schemes.Patient)
    async def get_item(
        patient_id: int,
        requesting_user: schemes.User = fastapi.Depends(
            access.get_confirmed_user
        ),
        session: sa_asyncio.AsyncSession = fastapi.Depends(
            sessions.create_session
        ),
    ):
        await access.validate_allowed_to_patient(
            requesting_user=requesting_user,
            patient_id=patient_id,
            loc=["path", "id"],
            patient_msg=texts.PATIENT_GET_HIMSELF,
            clinic_msg=texts.CLINIC_GET_PATIENTS,
            session=session,
        )
        patient = await session.get(
            models.Patient,
            patient_id,
            options=[
                sa.orm.joinedload(models.Patient.phone),
                sa.orm.joinedload(models.Patient.sex),
                sa.orm.joinedload(models.Patient.diagnosis),
            ],
            populate_existing=True,
        )
        return schemes.Patient.from_orm(patient)
