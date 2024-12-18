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
import threading
from yookassa import Configuration
from fastapi import APIRouter, Depends, HTTPException
from yookassa import Payment

from auth.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from auth.database import Users
from datetime import datetime, timedelta

#from payments.pay import router as payments_router
# Настройки RabbitMQ
RABBITMQ_HOST = 'localhost'
NEW_QUEUE_NAME = 'new_visits_queue'
Configuration.configure("996855", "test_Ea50FMw71gvcGgq-WGXcbmn74hCZCxm7DIC0jN9tvUw")

# Функция для получения subscription_end по id пользователя
async def get_subscription_end(user_id: int) -> datetime:
    async for session in get_async_session():
        result = await session.execute(select(Users.subscription_end).where(Users.id == user_id))
        subscription_end = result.scalar()
        return subscription_end


app = FastAPI(
    title="App"
)
#app.include_router(payments_router)
# Модель данных для ввода list_values
class PredictionInput(BaseModel):
    list_values: List[Union[int, float, str]]

@app.on_event("startup")
async def startup_event():
    await start_update_model_task()

fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

current_user = fastapi_users.current_user()

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

# Создаем глобальный цикл событий
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def run_event_loop():
    loop.run_forever()

# Запускаем цикл событий в отдельном потоке
threading.Thread(target=run_event_loop, daemon=True).start()

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


# Запуск потребителя RabbitMQ в отдельном потоке
threading.Thread(target=consume_from_rabbitmq, daemon=True).start()


"""@app.post("/subscribe")
async def subscribe(users: Users = Depends(current_user), session: AsyncSession = Depends(get_async_session)):
    if users.subscription_end and users.subscription_end > datetime.utcnow():
        return {"message": "Subscription is still active"}

    # Устанавливаем новую дату окончания подписки (на 30 дней вперед)
    new_subscription_end = datetime.utcnow() + timedelta(days=30)

    # Обновляем пользователя в базе данных
    await session.execute(
        Users.__table__.update()
        .where(Users.id == users.id)
        .values(subscription_end=new_subscription_end)
    )
    await session.commit()

    return {"message": "Subscription activated for 30 days"}"""



@app.post("/predict")
async def predict_endpoint(
        input_data: PredictionInput,
        users: Users = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    if not users.is_superuser:
        if not users.subscription_end or users.subscription_end < datetime.utcnow():
            raise HTTPException(status_code=403,
                                detail="Your subscription has expired. Please renew it to access this feature.")

    # Извлечение email из входных данных
    email = next((value for value in input_data.list_values if isinstance(value, str) and "@" in value), None)
    if not email:
        raise HTTPException(status_code=400, detail="Email is missing from the input data.")

    # Удаляем email из данных для предсказания
    filtered_data = [value for value in input_data.list_values if not (isinstance(value, str) and "@" in value)]

    # Получение предсказания модели
    prediction = get_model_prediction_with_input(filtered_data)
    print(prediction)
    confirmation = True
    if prediction == 1:
        confirmation = False
    print(filtered_data)
    filtered_data = [None if value == 0 else str(value) for value in filtered_data]
    # Запись сессии в базу данных
    time = datetime.utcnow()
    session_data = {
        "user_id": int(filtered_data[0]),
        "time1": filtered_data[2],
        "site1": filtered_data[1],
        "time2": filtered_data[4],
        "site2": filtered_data[3],
        "time3": filtered_data[6],
        "site3": filtered_data[5],
        "time4": filtered_data[8],
        "site4": filtered_data[7],
        "time5": filtered_data[10],
        "site5": filtered_data[9],
        "time6": filtered_data[12],
        "site6": filtered_data[11],
        "time7": filtered_data[14],
        "site7": filtered_data[13],
        "time8": filtered_data[16],
        "site8": filtered_data[15],
        "time9": filtered_data[18],
        "site9": filtered_data[17],
        "time10": filtered_data[20],
        "site10": filtered_data[19],
        "email": email,
        "target": prediction,
        "confirmation": confirmation,
        "date": time
    }

    await session.execute(insert(sessions).values(session_data))
    await session.commit()
    # Отправка уведомления при предсказании 0
    if not confirmation:
        subject = "Model Alert"
        body = f"На вашем аккаунте выполнены подозрительные действия. Вам следует сменить пароль. Помогите нам лучше распознавать подозрительные действия, перейдите по сыслке ""http://127.0.0.1:8000/docs#/default/check_session_check_session_get"" введите свою почту, это время " + str(time) + " и если вы согласны с предсказание введидте да, если не согласны, то введите нет"
        send_email(subject, body, email)

    return {"predictions": prediction}

async def predict_endpoint_auto(
        input_data: PredictionInput,
        #users: Users = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    # Извлечение email из входных данных
    email = next((value for value in input_data.list_values if isinstance(value, str) and "@" in value), None)
    if not email:
        raise HTTPException(status_code=400, detail="Email is missing from the input data.")

    # Удаляем email из данных для предсказания
    filtered_data = [value for value in input_data.list_values if not (isinstance(value, str) and "@" in value)]

    # Получение предсказания модели
    prediction = get_model_prediction_with_input(filtered_data)
    print(prediction)
    confirmation = True
    if prediction == 1:
        confirmation = False
    print(filtered_data)
    filtered_data = [None if value == 0 else str(value) for value in filtered_data]
    # Запись сессии в базу данных
    time = datetime.utcnow()
    session_data = {
        "user_id": int(filtered_data[0]),
        "time1": filtered_data[2],
        "site1": filtered_data[1],
        "time2": filtered_data[4],
        "site2": filtered_data[3],
        "time3": filtered_data[6],
        "site3": filtered_data[5],
        "time4": filtered_data[8],
        "site4": filtered_data[7],
        "time5": filtered_data[10],
        "site5": filtered_data[9],
        "time6": filtered_data[12],
        "site6": filtered_data[11],
        "time7": filtered_data[14],
        "site7": filtered_data[13],
        "time8": filtered_data[16],
        "site8": filtered_data[15],
        "time9": filtered_data[18],
        "site9": filtered_data[17],
        "time10": filtered_data[20],
        "site10": filtered_data[19],
        "email": email,
        "target": prediction,
        "confirmation": confirmation,
        "date": time
    }

    await session.execute(insert(sessions).values(session_data))
    await session.commit()

    # Отправка уведомления при предсказании 0
    if not confirmation:
        subject = "Model Alert"
        body = f"На вашем аккаунте выполнены подозрительные действия. Вам следует сменить пароль. Помогите нам лучше распознавать подозрительные действия, перейдите по сыслке ""http://127.0.0.1:8000/docs#/default/check_session_check_session_get"" введите свою почту, это время " + str(time) + " и если вы согласны с предсказание введидте да, если не согласны, то введите нет"
        send_email(subject, body, email)

    return {"predictions": prediction}

@app.get("/check-session")
async def check_session(
        email: str = Query(..., description="Email пользователя для проверки"),
        date: str = Query(..., description="Дата"),
        confirmation: str = Query(..., description="Подтверждение: да или нет"),
        session: AsyncSession = Depends(get_async_session)
):
    # Преобразуем 'confirmation' в логическое значение
    confirmation_bool = True if confirmation.lower() == "да" else False

    # Формируем запрос для проверки существующей сессии
    query = (
        select(sessions)
        .where(
            sessions.c.email == email,
            sessions.c.date.cast(String).like(f"{date}%"),
        )
    )
    result = await session.execute(query)
    session_entry = result.first()

    if not session_entry:
        return {"message": "Сессия не найдена"}

    # Проверка текущего статуса confirmation
    current_confirmation = session_entry[-2]
    if current_confirmation:
        return {"message": "Сессия уже подтверждена"}

    # Если 'confirmation' равно "нет", обновляем поле в базе данных
    if not confirmation_bool:
        update_query = (
            update(sessions)
            .where(
                sessions.c.email == email,
                sessions.c.date.cast(String).like(f"{date}%"),
            )
            .values(confirmation=True, target=0)
        )
        await session.execute(update_query)
        await session.commit()
        return {"message": "Сессия была обновлена и подтверждена"}

    if confirmation_bool:
        update_query = (
            update(sessions)
            .where(
                sessions.c.email == email,
                sessions.c.date.cast(String).like(f"{date}%"),
            )
            .values(confirmation=True, target=1)
        )
        await session.execute(update_query)
        await session.commit()
        return {"message": "Сессия была обновлена и подтверждена"}

    return {"message": "Мы рады, что помогли вам"}


@app.post("/create-payment")
async def create_payment(
    user: Users = Depends(current_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": "1000.00",
                    "currency": "RUB",
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "http://127.0.0.1:8000/payments/success",
                },
                "capture": True,
                "description": f"Subscription for user {user.id}",
                "metadata": {
                    "user_id": user.id,
                },
            }
        )

        # Используем реальный payment.id
        payment_id = payment.id
        print(f"User ID: {user.id}, Payment ID: {payment_id}")
        new_confirmation = False
        # Обновляем last_payment_id в таблице users
        await session.execute(
            text("UPDATE users SET payment_id = :payment_id, payment_confirmation= :val WHERE id = :user_id"),
            {"payment_id": payment.id, "user_id": user.id, "val": new_confirmation}
        )
        await session.commit()

        return {"confirmation_url": payment.confirmation.confirmation_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment creation failed: {e}")



@app.get("/payments/success")
async def payment_success(
    session: AsyncSession = Depends(get_async_session),
    user: Users = Depends(current_user),
):
    result = await session.execute(
        text("SELECT payment_confirmation FROM users WHERE id = :user_id"),
        {"user_id": user.id}
    )
    confirmation = result.scalar_one_or_none()
    print(confirmation)
    if confirmation:
        return {"message": "Payment not completed."}
        # Получаем информацию о платеже из YooKassa
    result = await session.execute(
        text("SELECT payment_id FROM users WHERE id = :user_id"),
        {"user_id": user.id}
    )
    payment_id = result.scalar_one_or_none()
    if payment_id == None:
        return {"message": "Payment not completed successfully."}
    payment = Payment.find_one(payment_id)
    if payment.status != "succeeded":
        return {"message": "Payment not completed successfully."}

        # Устанавливаем новую дату окончания подписки на 30 дней вперёд
    new_subscription_end = datetime.utcnow() + timedelta(days=30)

    await session.execute(
        Users.__table__.update()
        .where(Users.id == user.id)
        .values(subscription_end=new_subscription_end)
    )
    await session.commit()

    confirmation = True

    await session.execute(
        text("UPDATE users SET payment_confirmation = :payment WHERE id = :user_id"),
        {"payment": confirmation, "user_id": user.id}
    )
    await session.commit()

    return {"message": "Subscription activated for 30 days!"}



"""@app.post("/create-auto-payment")
async def create_auto_payment(
    user: Users = Depends(current_user),
):
    try:
        payment = Payment.create(
            {
                "amount": {
                    "value": "1000.00",
                    "currency": "RUB",
                },
                "payment_method_id": "CARD_TOKEN_FROM_USER",  # Токен карты пользователя
                "capture": True,
                "description": f"Auto-payment for user {user.id}",
                "metadata": {
                    "user_id": user.id,
                },
            }
        )

        return {"status": payment.status, "message": "Auto-payment initialized."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-payment creation failed: {e}")"""