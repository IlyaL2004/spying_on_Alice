import pytest
from ml_service.send_message_email.send_message import send_email


def test_send_email(mock_send_email):
    subject = "Test Subject"
    body = "Test Body"
    recipient = "recipient@example.com"

    try:
        send_email(subject, body, recipient)
    except Exception as e:
        assert str(e) == "Mocked exception"

