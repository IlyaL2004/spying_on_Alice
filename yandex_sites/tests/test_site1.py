import unittest
from flask import Flask, request, make_response
from unittest.mock import patch, MagicMock
import uuid
import os
from site1 import app, get_user_id, visit_site, load_visits, save_visits, ADMIN_SITES, USER_EMAILS, send_to_rabbitmq
from datetime import datetime


class TestFlaskApp(unittest.TestCase):
    
    @patch('site1.uuid.uuid4')
    def test_get_user_id_with_cookie(self, mock_uuid):
        """Тестируем, если user_id есть в cookies"""
        # Устанавливаем фейковое значение cookies
        mock_uuid.return_value = uuid.UUID('12345678-1234-1234-1234-123456789abc')

        with app.test_client() as client:
            # Отправляем запрос с cookies
            response = client.get('/admin1/site1', headers={'Cookie': 'user_id=existing-id'})
            
            self.assertEqual(response.status_code, 200)
            cookies = response.headers.getlist('Set-Cookie')
            # Проверяем наличие cookies в заголовке ответа
            self.assertTrue(any('user_id=existing-id' in cookie for cookie in cookies))

    @patch('site1.uuid.uuid4')
    def test_get_user_id_without_cookie(self, mock_uuid):
        """Тестируем генерацию нового user_id при отсутствии cookies"""
        mock_uuid.return_value = uuid.UUID('12345678-1234-1234-1234-123456789abc')

        with app.test_client() as client:
            # Запрос без cookies
            response = client.get('/admin1/site1')
            
            self.assertEqual(response.status_code, 200)
            cookies = response.headers.getlist('Set-Cookie')
            # Проверяем, что был установлен user_id
            self.assertTrue(any('user_id=12345678-1234-1234-1234-123456789abc' in cookie for cookie in cookies))


class TestFlaskApp(unittest.TestCase):
    
    @patch('site1.load_visits')
    @patch('site1.save_visits')
    def test_visit_site_success(self, mock_save_visits, mock_load_visits):
        """Тестируем успешное посещение сайта"""
        
        mock_load_visits.return_value = {}
        # Подготовка данных для теста
        ADMIN_SITES['admin1'] = ['site1']
        USER_EMAILS["12345678-1234-1234-1234-123456789abc"] = 'test@example.com'
        
        with app.test_client() as client:
            response = client.get('/admin1/site1', headers={'Cookie': 'user_id=12345678-1234-1234-1234-123456789abc'})
            
            self.assertEqual(response.status_code, 200)
            cookies = response.headers.getlist('Set-Cookie')
            self.assertTrue(any('user_id=' in cookie for cookie in cookies))  # Проверка на установку cookies
            mock_save_visits.assert_called_once()  # Проверяем, что сохранение данных посетителей произошло
            
    @patch('site1.load_visits')
    def test_visit_site_not_found(self, mock_load_visits):
        """Тестируем посещение несуществующего сайта"""
        mock_load_visits.return_value = {}
        ADMIN_SITES['admin1'] = ['site1']

        with app.test_client() as client:
            response = client.get('/admin1/non_existent_site')
            self.assertEqual(response.status_code, 404)
            self.assertIn(b"Site not found", response.data)

class TestRabbitMQ(unittest.TestCase):

    @patch('pika.BlockingConnection')
    def test_send_to_rabbitmq(self, MockBlockingConnection):
        """Тестируем отправку сообщения в RabbitMQ"""

        mock_connection = MagicMock()
        MockBlockingConnection.return_value = mock_connection
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        
        send_to_rabbitmq("test_message")

        mock_connection.channel.assert_called_once()
        mock_channel.basic_publish.assert_called_once_with(
            exchange='',
            routing_key='visits_queue',  # Проверьте, что QUEUE_NAME задано правильно
            body='test_message'
        )

if __name__ == '__main__':
    unittest.main()
