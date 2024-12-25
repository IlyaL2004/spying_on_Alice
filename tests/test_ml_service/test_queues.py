from unittest.mock import patch
from ml_service.queues.queues import send_to_queue, receive_from_queue

def test_send_to_queue():
    with patch("pika.BlockingConnection") as mock_connection:
        mock_channel = mock_connection.return_value.channel.return_value
        mock_channel.basic_publish.return_value = True
        result = send_to_queue("test_queue", {"data": "test"})
        assert result is True

def test_receive_from_queue():
    with patch("pika.BlockingConnection") as mock_connection:
        mock_channel = mock_connection.return_value.channel.return_value
        mock_channel.basic_get.return_value = ("", "", b'{"data": "test"}')
        result = receive_from_queue("test_queue")
        assert result == {"data": "test"}

