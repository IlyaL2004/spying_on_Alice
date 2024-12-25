import unittest
from unittest.mock import AsyncMock, patch
from fastapi_users import schemas, models, exceptions
from auth.menager import UserManager  # Импорт корректного пути к UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        # Инициализация mock базы данных
        self.mock_user_db = AsyncMock()
        self.user_manager = UserManager(self.mock_user_db)

    async def test_on_after_register(self):
        user = models.BaseUser(id=1, email="test@example.com", username="testuser", hashed_password="hashed_password")
        
        with patch("builtins.print") as mock_print:
            await self.user_manager.on_after_register(user)

        mock_print.assert_called_once_with("User 1 has registered.")

    async def test_create_user(self):
        user_create = schemas.UC(email="test@example.com", password="strongpassword")
        
        self.mock_user_db.get_by_email = AsyncMock(return_value=None)
        with patch.object(self.user_manager.password_helper, 'hash', return_value='hashed_password'):
            created_user = await self.user_manager.create(user_create)

        self.assertEqual(created_user.email, user_create.email)
        self.assertEqual(created_user.hashed_password, 'hashed_password')

    async def test_create_user_already_exists(self):
        user_create = schemas.UC(email="test@example.com", password="strongpassword")
        
        existing_user = models.BaseUser(id=1, email="test@example.com", username="testuser", hashed_password="hashed_password")
        self.mock_user_db.get_by_email = AsyncMock(return_value=existing_user)

        with self.assertRaises(exceptions.UserAlreadyExists):
            await self.user_manager.create(user_create)

if __name__ == "__main__":
    unittest.main()
