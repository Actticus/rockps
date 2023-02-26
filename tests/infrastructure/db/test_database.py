import pytest
import sqlalchemy as sa

from rockps.adapters import models


@pytest.mark.order(-1)
@pytest.mark.asyncio
async def test_database_is_empty(session):
    models_to_check = [
        models.Certificate,
        models.ConfirmationCode,
        models.Lobby,
        models.User,
        models.Phone,
    ]
    for model in models_to_check:
        result = await session.execute(
            sa.select(model)
        )
        assert not result.all()
