import pytest
from auth.database import Users


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = Users(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_pass",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    assert user.id is not None
    assert user.email == "test@example.com"

