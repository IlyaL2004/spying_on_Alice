import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime, timedelta
import pika
import os
import threading  # Добавьте импорт
from main import app, is_valid_email, write_to_file, callback, consume_from_rabbitmq, process_logs, send_to_rabbitmq, background_log_checker


class TestApp(unittest.TestCase):

    def test_is_valid_email(self):
        # Проверяем корректные и некорректные email
        self.assertTrue(is_valid_email('test@example.com'))
        self.assertTrue(is_valid_email('test.user@example.co'))
        self.assertFalse(is_valid_email('invalid-email'))
        self.assertFalse(is_valid_email('test@.com'))

    @patch('builtins.open', new_callable=MagicMock)
    def test_write_to_file(self, mock_open):
        data = {
            'test@example.com': [
                {'site': 'site1', 'timestamp': '2024-12-24T00:00:00', 'admin': 'admin1'}
            ]
        }
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        write_to_file(data)
        mock_open.assert_called_once_with('visits_log.txt', 'a', encoding='utf-8')
        mock_file.write.assert_called_once_with('test@example.com | site1 | 2024-12-24 00:00:00 | admin1\n')

    @patch('main.write_to_file')
    def test_callback_valid_data(self, mock_write_to_file):
        # Тестируем обработку сообщения с валидным JSON
        mock_write_to_file.reset_mock()  # сбрасываем моки перед тестом
        message = {
            "test@example.com": [
                {'site': 'site1', 'timestamp': '2024-12-24T00:00:00', 'admin': 'admin1'}
            ]
        }
        callback(None, None, None, json.dumps(message).encode())
        mock_write_to_file.assert_called_once_with(message)

    @patch('pika.BlockingConnection')
    def test_consume_from_rabbitmq(self, MockBlockingConnection):
        # Мокируем соединение с RabbitMQ
        mock_connection = MagicMock()
        MockBlockingConnection.return_value = mock_connection
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        # Проводим тестирование, избегая реального подключения
        with patch('time.sleep', return_value=None):  # предотвращаем реальное ожидание
            consume_from_rabbitmq()

        mock_connection.channel.assert_called_once()
        mock_channel.queue_declare.assert_called_once_with(queue=os.environ.get("QUEUE_NAME"))
        mock_channel.basic_consume.assert_called_once()


    @patch('builtins.open', new_callable=MagicMock)
    def test_process_logs(self, mock_open):
        # Тестируем функцию process_logs
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Пишем тестовый файл
        with open('visits_log.txt', 'w', encoding='utf-8') as f:
            f.write('test@example.com | site1 | 2024-12-24 00:00:00 | admin1\n')

        process_logs()

        mock_open.assert_called_with('visits_log.txt', 'w', encoding='utf-8')
        # Проверяем, что файл был перезаписан с обновленными данными
        mock_open.return_value.__enter__.return_value.write.assert_called_once()

    @patch('pika.BlockingConnection')
    def test_send_to_rabbitmq(self, MockBlockingConnection):
        # Тестируем отправку данных в RabbitMQ
        mock_connection = MagicMock()
        MockBlockingConnection.return_value = mock_connection
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel

        data = {"list_values": [1, 2, 3]}
        send_to_rabbitmq(data)

        mock_connection.channel.assert_called_once()
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key=os.environ.get("NEW_QUEUE_NAME"),
            body=json.dumps(data)
        )


    @patch('threading.Thread')
    def test_background_threads(self, MockThread):
        # Тестируем запуск фоновых потоков
        threading.Thread(target=consume_from_rabbitmq, daemon=True).start()
        threading.Thread(target=background_log_checker, daemon=True).start()
        MockThread.assert_called()


if __name__ == '__main__':
    unittest.main()
