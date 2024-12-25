from pydantic import BaseModel
from typing import List, Union
from sqlalchemy.future import select
import pika
import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from auth.database import get_async_session
from auth.database import Users
from datetime import datetime
from predict_and_confirmation_predict.predict_auto import predict_endpoint_auto
from models.models import users

RABBITMQ_HOST = 'localhost'
NEW_QUEUE_NAME = 'new_visits_queue'
class PredictionInput(BaseModel):
    list_values: List[Union[int, float, str]]
# Функция для получения subscription_end по id пользователя

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run_event_loop():
    loop.run_forever()

async def get_subscription_end(user_id: int) -> datetime:
    async for session in get_async_session():
        result = await session.execute(select(users.c.subscription_end).where(users.c.id == user_id))
        subscription_end = result.scalar()
        return subscription_end

# Функция для обработки сообщений и выполнения предсказаний
async def handle_prediction(data):
    # Получаем экземпляр асинхронной сессии из асинхронного генератора
    async for session in get_async_session():
        input_data = PredictionInput(list_values=data['list_values'])
        try:
            response = await predict_endpoint_auto(input_data=input_data, session=session)
            print("Результат предсказания:", response)
        except HTTPException as e:
            print(f"Ошибка при выполнении предсказания: {e.detail}")

# Callback для обработки сообщений из очереди
def callback(ch, method, properties, body):
    data = json.loads(body)
    print(data)
    data_admin = data
    list_values = data_admin['list_values']
    print(list_values[1])
    number_admin = list_values[1]

    if number_admin == 1:
        asyncio.run_coroutine_threadsafe(handle_prediction(data), loop)
    else:
        future = asyncio.run_coroutine_threadsafe(get_subscription_end(number_admin), loop)
        try:
            subscription_end = future.result()  # Дожидаемся результата асинхронной функции
        except Exception as e:
            print(f"Ошибка при получении подписки: {e}")
            return

        if not subscription_end or subscription_end < datetime.utcnow():
            print("Subscription has expired. Please renew it to access this feature.")
        else:
            asyncio.run_coroutine_threadsafe(handle_prediction(data), loop)


# Функция для подключения к RabbitMQ и запуска потребителя
def consume_from_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=NEW_QUEUE_NAME)
    channel.basic_consume(queue=NEW_QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print(" [*] Ожидание сообщений для предсказаний. Чтобы завершить, нажмите CTRL+C")
    channel.start_consuming()