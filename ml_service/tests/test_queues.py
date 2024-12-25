import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from queues.queues import get_subscription_end  # Импорт вашей функции

class TestGetSubscriptionEnd(unittest.TestCase):

    @patch('your_module.get_async_session')  # Патчим функцию get_async_session
    async def test_get_subscription_end_success(self, MockGetAsyncSession):
        # Создаём mock для сессии
        mock_session = MagicMock()
        MockGetAsyncSession.return_value = [mock_session]  # Мокируем возврат сессии

        # Предположим, что для пользователя с id = 1 будет возвращена дата окончания подписки
        user_id = 1
        subscription_end_date = datetime(2024, 12, 31)
        
        # Мокируем выполнение запроса
        mock_result = MagicMock()
        mock_result.scalar.return_value = subscription_end_date
        mock_session.execute.return_value = mock_result

        # Вызываем функцию
        result = await get_subscription_end(user_id)

        # Проверяем, что результат совпадает с ожидаемым
        self.assertEqual(result, subscription_end_date)

        # Проверяем, что запрос был выполнен с правильным пользователем
        mock_session.execute.assert_called_once_with(
            select(Users.subscription_end).where(Users.id == user_id)
        )

    @patch('your_module.get_async_session')  # Патчим функцию get_async_session
    async def test_get_subscription_end_user_not_found(self, MockGetAsyncSession):
        # Создаём mock для сессии
        mock_session = MagicMock()
        MockGetAsyncSession.return_value = [mock_session]  # Мокируем возврат сессии

        # Предположим, что для пользователя с id = 9999 подписка не найдена
        user_id = 9999
        
        # Мокируем выполнение запроса, возвращаем None
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        mock_session.execute.return_value = mock_result

        # Вызываем функцию
        result = await get_subscription_end(user_id)

        # Проверяем, что результат равен None
        self.assertIsNone(result)

        # Проверяем, что запрос был выполнен с правильным пользователем
        mock_session.execute.assert_called_once_with(
            select(Users.subscription_end).where(Users.id == user_id)
        )

if __name__ == '__main__':
    unittest.main()
