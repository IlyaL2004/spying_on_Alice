import pytest
from fastapi.testclient import TestClient
from auth.database import Users
from auth.database import get_async_session


@pytest.mark.asyncio
async def test_predict_endpoint(test_client, db_session):
    user = Users(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_pass",
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    data = {
        "list_values": [1, "google.com", "2023-01-01 12:00:00"] + [0] * 18
    }
    response = test_client.post("/predict", json=data)
    assert response.status_code == 200
    assert "predictions" in response.json()

