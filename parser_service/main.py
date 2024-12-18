from textwrap import indent

from fastapi import FastAPI
import pika
import time
import json
import threading
import re
from datetime import datetime, timedelta
from time import sleep

app = FastAPI()

# Настройка подключения к RabbitMQ
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'visits_queue'
OUTPUT_FILE = 'visits_log.txt'


def is_valid_email(email):
    """Проверяет, является ли строка корректным email."""
    email_pattern = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_pattern, email) is not None


def write_to_file(data):
    """Записывает данные в текстовый файл в формате 'почта | сайт | время | админ', если email корректен"""
    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        for email, visits in data.items():
            if not is_valid_email(email):
                print(f"Некорректный email: {email} — запись пропущена")
                continue  # Пропустить запись, если email некорректен

            for visit in visits:
                # Приводим время к формату 'YYYY-MM-DD HH:MM:SS'
                formatted_time = datetime.fromisoformat(visit['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                line = f"{email} | {visit['site']} | {formatted_time} | {visit['admin']}\n"
                print(line)
                f.write(line)


def callback(ch, method, properties, body):
    """Callback-функция для обработки сообщений из RabbitMQ"""
    try:
        data = json.loads(body)
        write_to_file(data)
        print("Данные записаны в visits_log.txt")
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON")




"""def consume_from_rabbitmq():
    RABBITMQ_HOST = 'localhost'
    attempts = 10
    delay = 5

    for attempt in range(attempts):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
            print(" [*] Ожидание сообщений. Чтобы завершить, нажмите CTRL+C")
            channel.start_consuming()
            print("Подключение к RabbitMQ успешно")
            break
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Попытка {attempt + 1} подключения не удалась: {e}")
            time.sleep(delay)
    else:
        print("Не удалось подключиться к RabbitMQ после нескольких попыток.")"""


def consume_from_rabbitmq():
    #Подключение к RabbitMQ и потребление сообщений из очереди
    time.sleep(20)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print(" [*] Ожидание сообщений. Чтобы завершить, нажмите CTRL+C")
    channel.start_consuming()


import json
from datetime import datetime, timedelta

OUTPUT_FILE = 'visits_log.txt'



import pika
import json

RABBITMQ_HOST = 'localhost'
NEW_QUEUE_NAME = 'new_visits_queue'

def send_to_rabbitmq(data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=NEW_QUEUE_NAME)
    channel.basic_publish(exchange='', routing_key=NEW_QUEUE_NAME, body=json.dumps(data))
    connection.close()



def process_logs():
    """Обрабатывает логи, учитывая только записи старше 3 минут, собирает до 10 записей и выводит их по отдельности в формате JSON."""
    current_time = datetime.utcnow()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    current_time = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    current_time = current_time + timedelta(hours=3)
    # Читаем все строки из файла
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    grouped_data = {}
    remaining_lines = []
    for line in lines:
        parts = line.strip().split(' | ')
        if len(parts) != 4:
            continue  # Пропуск некорректных строк

        email, site, timestamp, admin = parts

        try:
            visit_time = datetime.fromisoformat(timestamp)
        except ValueError:
            continue  # Пропуск строк с некорректной датой

        # Проверка, старше ли запись 3 минут
        #print(current_time)
        #print(visit_time)
        #print(abs(current_time - visit_time))
        #print(abs(current_time - visit_time) < timedelta(minutes=1))
        if abs(current_time - visit_time) < timedelta(minutes=1):
            remaining_lines.append(line)
            continue  # Просто пропускаем запись

        # Извлечение цифры из admin (например, admin1 -> 1, admin2 -> 2)
        admin_number = int(admin[-1])

        # Формирование ключа для группировки
        key = (email, admin_number)
        if key not in grouped_data:
            grouped_data[key] = []
        # Добавление данных в группу
        grouped_data[key].append((int(site), timestamp))

    # Формирование результата в требуемом формате
    for (email, admin_number), visits in grouped_data.items():
        # Берём только первые 10 записей
        selected_visits = visits[:10]
        list_values = [email, admin_number]

        # Добавление данных из записей
        for site, timestamp in selected_visits:
            list_values.append(site)
            list_values.append(timestamp)

        # Заполнение недостающих значений нулями до длины 22 элементов
        while len(list_values) < 22:
            list_values.append(0)

        # Обрезка, если длина превышает 22 элемента
        list_values = list_values[:22]

        #send_to_rabbitmq(data)
        # Вывод каждого JSON-объекта отдельно
        result = {"list_values": list_values}
        #print(json.dumps(result, indent=2, ensure_ascii=False))
        #for element in list_values:
        #    print(1111111111)
        print("send")
        send_to_rabbitmq(result)
        #    print(element)


    # Перезапись файла только с записями моложе 3 минут
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for line in remaining_lines:
            f.write(line)


def background_log_checker():
    """Фоновый процесс для проверки логов каждые 60 секунд."""
    while True:
        process_logs()
        sleep(15)  # Интервал проверки (60 секунд)


# Запуск потребителя RabbitMQ в отдельном потоке
threading.Thread(target=consume_from_rabbitmq, daemon=True).start()
# Запуск фоновой проверки логов в отдельном потоке
threading.Thread(target=background_log_checker, daemon=True).start()


@app.get("/")
def read_root():
    return {"message": "FastAPI приложение работает и слушает RabbitMQ"}