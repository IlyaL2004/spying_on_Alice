from pydantic import BaseModel
from typing import List, Union
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate
from ml_model.background_tasks import start_update_model_task
from fastapi import FastAPI, Query, Depends, HTTPException
import threading
from auth.database import Users
from payments.pay import router as payments_router
from predict_and_confirmation_predict.predict_and_confirmation import predict_and_confirmation_router
from queues.queues import run_event_loop
from queues.queues import consume_from_rabbitmq
import time

app = FastAPI(
    title="App"
)
app.include_router(payments_router)
app.include_router(predict_and_confirmation_router)
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

# start_rabbitMQ = False

# while not start_rabbitMQ:
#     try:
#         # Запускаем цикл событий в отдельном потоке
#         threading.Thread(target=run_event_loop, daemon=True).start()

#         # Запуск потребителя RabbitMQ в отдельном потоке
#         threading.Thread(target=consume_from_rabbitmq, daemon=True).start()

#         start_rabbitMQ = True
#     except:
#         time.sleep(60)


# time.sleep(200) #(?)

# Запускаем цикл событий в отдельном потоке
threading.Thread(target=run_event_loop, daemon=True).start()

# Запуск потребителя RabbitMQ в отдельном потоке
threading.Thread(target=consume_from_rabbitmq, daemon=True).start()
