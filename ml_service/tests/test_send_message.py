import unittest
from unittest.mock import patch, MagicMock
import smtplib
from send_message_email.send_message import send_email

TEST_EMAIL = "test@example.com"
TEST_PASS = "testpassword"

class TestEmailSender(unittest.TestCase):

    @patch('smtplib.SMTP')
    @patch('send_message_email.send_message.SENDER_EMAIL', TEST_EMAIL)
    @patch('send_message_email.send_message.SENDER_PASSWORD', TEST_PASS)
    def test_send_email_success(self, mock_smtp):
        subject = "Test Subject"
        body = "This is a test email."
        recipient_email = "recipient@example.com"

        # Создаем объект mock для SMTP-сервера
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        # Вызываем функцию отправки письма
        send_email(subject, body, recipient_email)

        # Проверяем вызовы функций
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(TEST_EMAIL, TEST_PASS)
        mock_server.send_message.assert_called_once()


if __name__ == "__main__":
    unittest.main()
