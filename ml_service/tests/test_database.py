import unittest
from unittest.mock import AsyncMock, patch
from auth.database import get_async_session, get_user_db, Users
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

class TestDatabaseModule(unittest.IsolatedAsyncioTestCase):
    @patch("auth.database.async_session_maker")
    async def test_get_async_session(self, mock_async_session_maker):
        mock_session = AsyncMock()
        mock_async_session_maker.return_value.__aenter__.return_value = mock_session  
        mock_async_session_maker.return_value.__aexit__.return_value = None 

        async for session in get_async_session():
            self.assertIs(session, mock_session)

    @patch("auth.database.async_session_maker")
    async def test_get_user_db(self, mock_async_session_maker):
        mock_session = AsyncMock()
        mock_async_session_maker.return_value.__aenter__.return_value = mock_session
        mock_async_session_maker.return_value.__aexit__.return_value = None
        mock_user_db = SQLAlchemyUserDatabase(mock_session, Users)

        with patch('auth.database.SQLAlchemyUserDatabase', return_value=mock_user_db):
            async for session in get_async_session():  # Используем async for для обработки генератора
                async for user_db in get_user_db(session):
                    self.assertIs(user_db, mock_user_db)


if __name__ == "__main__":
    unittest.main()
