from unittest.mock import patch
from ml_service.auth.auth import authenticate_user

def test_authenticate_user_success():
    with patch("ml_service.auth.database.get_user") as mock_get_user:
        mock_get_user.return_value = {"username": "test", "password": "hashed_pass"}
        result = authenticate_user("test", "password")
        assert result is not None

def test_authenticate_user_failure():
    with patch("ml_service.auth.database.get_user") as mock_get_user:
        mock_get_user.return_value = None
        result = authenticate_user("test", "password")
        assert result is None

