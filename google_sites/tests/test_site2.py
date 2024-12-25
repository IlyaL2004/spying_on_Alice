import unittest
from flask import Flask, request, make_response
from unittest.mock import patch, MagicMock
import json
import os
import uuid
import pika
from unittest.mock import patch, MagicMock

from site2 import app, ADMIN_SITES, load_visits, save_visits, get_user_id, send_to_rabbitmq

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        """Настройка тестов"""
        self.client = app.test_client()

        # Очистим словарь перед каждым тестом
        ADMIN_SITES.clear()

    @patch('site2.load_visits')
    def test_visit_site_success(self, mock_load_visits):
        # Настроить mock для load_visits
        mock_load_visits.return_value = {
            'ilyalarin2021@gmail.com': [{'site': 'site1', 'timestamp': '2024-12-24T00:00:00', 'admin': 'admin1'}]
        }
        response = self.client.get('/admin1/site1')
        self.assertIn('ilyalarin2021@gmail.com', mock_load_visits())


    @patch('site2.load_visits')
    def test_visit_site_not_found(self, mock_load):
        """Тестирование посещения несуществующего сайта"""

        # Инициализируем данные для теста
        admin_list = ['admin1']
        ADMIN_SITES['admin1'] = ['site1']
        mock_load.return_value = {}

        with self.client:
            response = self.client.get('/admin1/non_existent_site')

            self.assertEqual(response.status_code, 404)
            self.assertIn(b"Site not found", response.data)

    @patch('pika.BlockingConnection')
    def test_send_to_rabbitmq(self, MockBlockingConnection):
        # Настроить mock-объект
        mock_connection = MagicMock()
        MockBlockingConnection.return_value = mock_connection
        # Теперь тестируем send_to_rabbitmq
        send_to_rabbitmq("test_message")
        mock_connection.channel.assert_called_once()


    @patch('pika.BlockingConnection')
    def test_rabbitmq_connection(self, MockConnection):
        """Тестирование подключения к RabbitMQ"""

        # Мокаем поведение RabbitMQ
        mock_channel = MagicMock()
        mock_connection = MagicMock()
        mock_connection.channel.return_value = mock_channel
        MockConnection.return_value = mock_connection

        # Используем mock для RABBITMQ_HOST, чтобы тесты использовали localhost
        with patch.dict('os.environ', {'RABBITMQ_HOST': 'rabbitmq'}):  # Замените 'localhost' на 'rabbitmq', если это нужно
            send_to_rabbitmq('test_message')

        # Проверим, что подключение к RabbitMQ было выполнено с правильным хостом
        MockConnection.assert_called_once_with(pika.ConnectionParameters('rabbitmq'))  # Или 'localhost', если измените в тесте
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key=os.environ.get("QUEUE_NAME"),
            body='test_message'
        )



    def tearDown(self):
        """Очистка после тестов"""
        pass

if __name__ == '__main__':
    unittest.main()
