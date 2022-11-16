from typing import AsyncGenerator

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from rockps.adapters import engines


def get_session_class(isolation_level):
    engine = engines.Database.get(isolation_level)
    return sa.orm.sessionmaker(
        engine,
        expire_on_commit=False,
        class_=sa_asyncio.AsyncSession,
    )


async def create_session(
    isolation_level: str = "default",
) -> AsyncGenerator[sa_asyncio.AsyncSession, None]:
    session_class = get_session_class(isolation_level)
    session: sa_asyncio.AsyncSession = session_class()

    try:
        yield session
    except Exception as e:
        await session.rollback()  # pragma: nocover
        await session.close()  # pragma: nocover
        raise e  # pragma: nocover
    await session.commit()
    await session.close()
