from auth.database import get_async_session, Users
from yookassa import Configuration, Payment
from fastapi import APIRouter, Depends, HTTPException
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.menager import get_user_manager
from config import YOOKASSA_KEY, YOOKASSA_SHOP_ID
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from models.models import users
from sqlalchemy import select, update
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

router = APIRouter()
fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)
current_user = fastapi_users.current_user()
Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_KEY)
# Определение базы данных
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Создание асинхронного движка и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
async def get_users_with_expiring_subscriptions():
    try:
        # Вычисляем дату через 30 дней
        target_date = datetime.utcnow() + timedelta(days=3)
        async with AsyncSessionLocal() as session:
        # Запрос для поиска пользователей
            stmt = select(users).where(
                users.c.subscription_end <= target_date,
                users.c.payment_auto == True
            )
            result = await session.execute(stmt)
        # Получаем список пользователей
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print(f"X_train shape: {df.shape}")
        return df
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error fetching users: {e}")
async def update_subscriptions():
    #while True:
    users = await get_users_with_expiring_subscriptions()
        # Итерация по строкам
    for row in users.itertuples(index=True):
        pay_id = await create_auto_payment(row.id, row.payment_method_id)
        print(pay_id)
        payment = Payment.find_one(pay_id)
        if payment.status == "succeeded":
            print("Payment was successful!")
            await update_date(row.id)
        elif payment.status == "pending":
            print("Payment is pending.")
        else:
            print(f"Payment failed with status: {payment.status}")
        #await asyncio.sleep(43200)
async def create_auto_payment(user_id: int, payment_method_id):
    try:
        # Создаём автоплатёж
        payment = Payment.create(
            {
                "amount": {
                    "value": "1000.00",
                    "currency": "RUB",
                },
                "capture": True,
                "description": f"Autopayment for user {user_id}",
                "payment_method_id": payment_method_id,  # Используем сохранённый ID
            }
        )
        return payment.id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autopayment creation failed: {e}")
async def update_date(user_id):
    new_subscription_end = datetime.utcnow() + timedelta(days=33)
    async with AsyncSessionLocal() as session:
        try:
            # Запрос для обновления даты окончания подписки
            stmt = (
                update(users)
                .where(users.c.id == user_id)
                .values(subscription_end=new_subscription_end)
            )
            await session.execute(stmt)
            await session.commit()  # Подтверждение изменений
            return {"status": "success", "new_subscription_end": new_subscription_end}
        except Exception as e:
            await session.rollback()  # Откат изменений в случае ошибки
            raise e