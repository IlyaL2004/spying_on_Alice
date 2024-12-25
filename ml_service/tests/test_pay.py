import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from payments.pay import router  # Предположительно, ваш файл называется payments.py
from auth.database import Users
from datetime import datetime, timedelta
from payments.pay import Payment
from payments.pay import current_user



class TestPaymentRoutes(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(router)  # Инициализация клиента FastAPI

    @patch("payments.Payment.create")
    @patch("payments.get_async_session")
    @patch("payments.current_user")
    async def test_create_payment_success(
        self, mock_current_user, mock_get_async_session, mock_payment_create
    ):
        # Mock текущего пользователя
        mock_user = Users(id=1, username="testuser")
        mock_current_user.return_value = mock_user

        # Mock базы данных
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_async_session.return_value = mock_session

        # Mock ответа от YooKassa
        mock_payment_create.return_value = AsyncMock(
            id="payment_id_123",
            confirmation=AsyncMock(confirmation_url="http://example.com/confirmation"),
        )

        response = self.client.post("/create-payment")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"confirmation_url": "http://example.com/confirmation"},
        )
        mock_payment_create.assert_called_once()
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch("payments.Payment.find_one")
    @patch("payments.get_async_session")
    @patch("payments.current_user")
    async def test_payment_success_subscription_activated(
        self, mock_current_user, mock_get_async_session, mock_find_one
    ):
        # Mock текущего пользователя
        mock_user = Users(id=1, username="testuser", subscription_end=None)
        mock_current_user.return_value = mock_user

        # Mock базы данных
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = [
            AsyncMock(scalar_one_or_none=AsyncMock(return_value=False)),  # payment_confirmation
            AsyncMock(scalar_one_or_none=AsyncMock(return_value="payment_id_123")),  # payment_id
        ]
        mock_get_async_session.return_value = mock_session

        # Mock ответа от YooKassa
        mock_find_one.return_value = AsyncMock(status="succeeded")

        response = self.client.get("/payments/success")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"message": "Subscription activated for 30 days!"},
        )
        mock_find_one.assert_called_once()
        mock_session.commit.assert_called()

    @patch("payments.get_async_session")
    @patch("payments.current_user")
    async def test_payment_success_not_completed(
        self, mock_current_user, mock_get_async_session
    ):
        # Mock текущего пользователя
        mock_user = Users(id=1, username="testuser", subscription_end=None)
        mock_current_user.return_value = mock_user

        # Mock базы данных
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute.side_effect = [
            AsyncMock(scalar_one_or_none=AsyncMock(return_value=True)),  # payment_confirmation
        ]
        mock_get_async_session.return_value = mock_session

        response = self.client.get("/payments/success")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Payment not completed."})

    @patch("payments.Payment.create")
    async def test_create_payment_failure(self, mock_payment_create):
        mock_payment_create.side_effect = Exception("Payment creation failed")

        response = self.client.post("/create-payment")

        self.assertEqual(response.status_code, 500)
        self.assertIn("Payment creation failed", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
