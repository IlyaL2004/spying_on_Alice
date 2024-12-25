from unittest.mock import patch
from parser_service.main import process_data

def test_process_data_valid():
    with patch("parser_service.queues.send_to_queue") as mock_queue:
        mock_queue.return_value = True
        result = process_data({"site": "example.com", "timestamp": "2023-01-01 12:00:00"})
        assert result is True

def test_process_data_invalid():
    result = process_data({"invalid_key": "value"})
    assert result is False

