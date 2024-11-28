from datetime import datetime, timedelta
from fastapi import FastAPI, Depends

from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.database import Users, get_async_session
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate

from ml_model.model import get_model_prediction, load_model
from ml_model.background_tasks import start_update_model_task
from send_message_email.send_message import send_email
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.database import get_async_session
from auth.database import Users

app = FastAPI(
    title="App"
)

@app.on_event("startup")
async def startup_event():
    # Загрузка модели при старте приложения
    load_model()
    # Запускаем фоновую задачу обновления модели
    start_update_model_task()


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


@app.post("/subscribe")
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

    return {"message": "Subscription activated for 30 days"}


@app.get("/predict")
async def predict_endpoint(users: Users = Depends(current_user)):
    # Проверка, является ли пользователь администратором
    if not users.is_superuser:
        # Если пользователь не администратор, проверяем статус подписки
        if not users.subscription_end or users.subscription_end < datetime.utcnow():
            return {"error": "Your subscription has expired. Please renew it to access this feature."}

    prediction = get_model_prediction()
    subject = "Статус предсказания модели"
    body = f"Модель завершила предсказание. Результат: {prediction}"
    # Отправка уведомления на почту
    send_email(subject, body)
    return {"predictions": prediction}



@app.get("/protected-route")
def protected_route(users: Users = Depends(current_user)):
    return f"Hello, {users.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"
