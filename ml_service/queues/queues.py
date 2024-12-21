

from pydantic import BaseModel
from typing import List, Union
from sqlalchemy import insert, String, text
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate
from ml_model.background_tasks import start_update_model_task
from send_message_email.send_message import send_email
from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.types import String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.database import Users
import pika
import json
from ml_model.model import get_model_prediction_with_input
from sqlalchemy import insert
from auth.database import get_async_session
from models.models import sessions
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from yookassa import Payment
from config import YOOKASSA_KEY
from config import YOOKASSA_SHOP_ID
from config import RABBITMQ_HOST, NEW_QUEUE_NAME
from auth.database import get_async_session
from auth.database import Users
from datetime import datetime, timedelta
from predict_and_confirmation_predict.predict_auto import predict_endpoint_auto
import time
from time import sleep

class PredictionInput(BaseModel):
    list_values: List[Union[int, float, str]]
# Функция для получения subscription_end по id пользователя

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run_event_loop():
    loop.run_forever()

async def get_subscription_end(user_id: int) -> datetime:
    async for session in get_async_session():
        result = await session.execute(select(Users.subscription_end).where(Users.id == user_id))
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
    time.sleep(20)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=NEW_QUEUE_NAME)
    channel.basic_consume(queue=NEW_QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print(" [*] Ожидание сообщений для предсказаний. Чтобы завершить, нажмите CTRL+C")
    channel.start_consuming()