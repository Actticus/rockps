from collections.abc import AsyncGenerator

from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession

from rockps.adapters import engines


def get_session_class(isolation_level):
    engine = engines.Database.get(isolation_level)
    return orm.sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def create_session(
    isolation_level: str = "default",
) -> AsyncGenerator[AsyncSession, None]:
    session_class = get_session_class(isolation_level)
    session: AsyncSession = session_class()

    try:
        yield session
    except Exception as e:
        await session.rollback()
        await session.close()
        raise e
    await session.commit()
    await session.close()
