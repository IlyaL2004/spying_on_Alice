from pydantic import BaseModel

from fastapi import FastAPI, Depends, BackgroundTasks

from fastapi_users import fastapi_users, FastAPIUsers
from auth.auth import auth_backend
from auth.database import Users
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate

from ml_model.model import get_model_prediction, load_model
from ml_model.background_tasks import start_update_model_task
from send_message_email.send_message import send_email


app = FastAPI(
    title="App"
)

@app.on_event("startup")
async def startup_event():
    # Загрузка модели при старте приложения
    load_model()
    # Запускаем фоновую задачу обновления модели
    start_update_model_task()

@app.get("/predict")
async def predict_endpoint():
    prediction = get_model_prediction()
    subject = "Статус предсказания модели"
    body = f"Модель завершила предсказание. Результат: {prediction}"
    # Отправка уведомления на почту
    send_email(subject, body)
    return {"predictions": prediction}


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

@app.get("/protected-route")
def protected_route(users: Users = Depends(current_user)):
    return f"Hello, {users.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"










