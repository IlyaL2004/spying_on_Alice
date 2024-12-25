import pytest
from auth.manager import UserManager
from auth.database import Users


@pytest.mark.asyncio
async def test_create_user(mock_send_email, db_session):
    user_manager = UserManager(db_session)
    user_data = {
        "email": "test@example.com",
        "password": "test_password",
    }

    user = await user_manager.create(user_data)
    assert user.email == "test@example.com"
    assert user.hashed_password is not None

