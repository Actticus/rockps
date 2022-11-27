# pylint: disable=redefined-outer-name, unused-argument
import asyncio
import datetime
import random
import string

import async_asgi_testclient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_scoped_session

import rockps
from rockps import consts
from rockps import settings
from rockps.adapters import models
from rockps.adapters import services
from rockps.adapters import sessions

# Сonsole options


def pytest_addoption(parser):
    parser.addoption(
        "--unmock-call",
        action="store_true",
        default=False,
        help="Don't mock call service's requests.",
    )


@pytest_asyncio.fixture(scope='session')
async def session_factory():
    return async_scoped_session(
        sessions.get_session_class(),
        asyncio.current_task,
    )


@pytest_asyncio.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
def app():
    yield rockps.init()


@pytest_asyncio.fixture(scope='session')
async def client(app):
    test_client = async_asgi_testclient.TestClient
    async with test_client(app) as _client:
        yield _client


@pytest_asyncio.fixture(scope='function')
async def session(session_factory):
    session: AsyncSession = session_factory()

    yield session

    await session.rollback()
    await session.close()


@pytest_asyncio.fixture
def mock_call_service(monkeypatch, pytestconfig):

    async def mocked_call(*_, **__):
        return '2363551521608028570'

    if not pytestconfig.getoption("--unmock-call"):
        monkeypatch.setattr(
            services.external.call,
            "call",
            mocked_call,
        )
    yield

# Database fixtures


@pytest_asyncio.fixture
async def admin_phone(client, session: AsyncSession):
    obj = models.Phone(
        number=settings.ADMIN_PHONE,
        is_confirmed=True,
    )

    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    yield obj
    await session.delete(obj)
    await session.commit()


@pytest_asyncio.fixture
async def confirmed_phone(client, session: AsyncSession):
    obj = models.Phone(
        number="+79111111111",
        is_confirmed=True,
    )

    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    yield obj
    await session.delete(obj)
    await session.commit()


@pytest_asyncio.fixture
async def unconfirmed_phone(
    client,
    session: AsyncSession
):
    obj = models.Phone(
        number="+79000000000",
        is_confirmed=False,
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    yield obj
    await session.delete(obj)
    await session.commit()


@pytest_asyncio.fixture
async def user(
    admin_phone,
    session: AsyncSession,
):
    obj = models.User(
        phone=admin_phone,
        nickname="John Cena",
        birth_date=datetime.datetime.now(),
        sex_id=consts.Sex.MALE,
    )
    obj.set_password("qwerty123")

    session.add(obj)
    await session.commit()
    await session.refresh(obj, ["id"])
    yield obj
    await session.delete(obj)
    await session.commit()


@pytest_asyncio.fixture
async def unconfirmed_user(
    unconfirmed_phone,
    session: AsyncSession
):
    obj = models.User(
        phone=unconfirmed_phone,
        nickname="John Cena",
        birth_date=datetime.datetime.now(),
        sex_id=consts.Sex.MALE,
    )
    obj.set_password("qwerty123")

    session.add(obj)
    await session.commit()
    await session.refresh(obj, ["id"])
    yield obj
    await session.delete(obj)
    await session.commit()


@pytest_asyncio.fixture
async def confirmation_code(
    unconfirmed_patient,
    session: AsyncSession
):
    obj = models.ConfirmationCode(
        value=''.join(random.choice(string.digits) for _ in range(4)),
        phone_id=unconfirmed_patient.phone_id,
        type_id=consts.ConfirmationCodeType.CONFIRM,
    )

    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    yield obj


@pytest_asyncio.fixture
async def lobby(
    user,
    session: AsyncSession
):
    obj = models.Lobby(
        name="Test lobby",
        is_public=True,
        max_players=3,
        creator_id=user.id,
    )

    session.add(obj)
    await session.flush()
    await session.refresh(obj)
    user.lobby_id = obj.id
    await session.commit()
    yield obj
    await session.delete(obj)
    await session.commit()


@pytest_asyncio.fixture
async def reset_code(
    user,
    session: AsyncSession,
):
    obj = models.ConfirmationCode(
        value=''.join(random.choice(string.digits) for _ in range(4)),
        phone=user.phone,
        type_id=consts.ConfirmationCodeType.RESET,
    )

    session.add(obj)
    await session.commit()
    await session.refresh(obj, ["id"])
    yield obj


@pytest_asyncio.fixture
async def certificate(user, session: AsyncSession):
    obj = models.Certificate(user=user)

    session.add(obj)
    await session.commit()
    await session.refresh(obj, ["id"])
    yield obj
    await session.delete(obj)
    await session.commit()
