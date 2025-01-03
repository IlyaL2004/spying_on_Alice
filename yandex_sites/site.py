from flask import Flask, request, make_response
from datetime import datetime
import uuid
import json
import os
import pika
import threading
import time
from dotenv import load_dotenv
import os


app = Flask(__name__)

# Настройка подключения к RabbitMQ
load_dotenv()
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")
QUEUE_NAME = os.environ.get("QUEUE_NAME")

def send_to_rabbitmq(message):
    """Отправка сообщения в RabbitMQ"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
    connection.close()

# Функция для генерации сайтов для админа
def generate_admin_sites():
    return [f"{i}" for i in range(1, 17)]

# Словарь для хранения сайтов админов
ADMIN_SITES = {}

def initialize_admin_sites(admin_list):
    """Инициализация сайтов для каждого админа"""
    for admin_id in admin_list:
        ADMIN_SITES[admin_id] = generate_admin_sites()

DATA_FILE = 'visits.json'

# Словарь для соответствия user_id и почты
USER_EMAILS = {
    "ac6d5844-f8c7-4715-91ab-a628c8462c70": "ilyalarin2021@gmail.com",
    "67a86189-eede-4d71-8166-07db226ac145": "ilalarin467@gmail.com",
    "31bffd61-ee5d-4636-8d28-349c0b43d499": "ilyalarin2021@gmail.com",
}

def load_visits():
    """Загрузка данных посещений из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_visits(visits):
    """Сохранение данных посещений в файл"""
    with open(DATA_FILE, 'w') as f:
        json.dump(visits, f)

def get_user_id(request):
    """Получение user_id из куки или создание нового"""
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id

@app.route('/<admin_id>/<site_name>')
def visit_site(admin_id, site_name):
    """Обработка посещения сайта"""
    if admin_id not in ADMIN_SITES or site_name not in ADMIN_SITES[admin_id]:
        return "Site not found", 404

    user_id = get_user_id(request)
    email = USER_EMAILS.get(user_id, user_id)
    timestamp = datetime.now().isoformat()

    visits = load_visits()

    if email not in visits:
        visits[email] = []

    # Добавляем новое посещение с информацией об админе
    visits[email].insert(0, {
        'site': site_name,
        'timestamp': timestamp,
        'admin': admin_id  # Добавляем администратора
    })

    save_visits(visits)

    response = make_response(f"Visiting {site_name}")
    response.set_cookie('user_id', user_id, max_age=60 * 60 * 24 * 365)
    return response

def send_and_clear_visits_periodically():
    """Функция для периодической отправки накопленных данных в RabbitMQ и очистки файла"""
    while True:
        time.sleep(30)  # Интервал в 15 секунд

        visits = load_visits()

        if visits:
            # Отправляем данные в RabbitMQ
            message = json.dumps(visits)
            send_to_rabbitmq(message)

            # Очищаем файл после отправки
            save_visits({})  # Очистка данных

            print("Sent and cleared accumulated visits.")

if __name__ == '__main__':
    # Пример инициализации для списка админов
    admin_list = ['admin2']
    initialize_admin_sites(admin_list)

    # Запуск фоново потока для отправки накопленных данных
    threading.Thread(target=send_and_clear_visits_periodically, daemon=True).start()
    #port = int(os.getenv('FLASK_RUN_PORT', 5001))  # Получить порт из переменной окружения
    app.run(debug=True, host='0.0.0.0', port=5001)