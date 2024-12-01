from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Union

from sqlalchemy import insert, String

from models.models import sessions
from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.database import Users, get_async_session
from auth.menager import get_user_manager
from auth.schemas import UserRead, UserCreate

from ml_model.model import get_model_prediction_with_input, load_model, load_and_preprocess_data, train_or_update_model, \
    save_model
from ml_model.background_tasks import start_update_model_task
from send_message_email.send_message import send_email
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth.database import get_async_session
from auth.database import Users
from fastapi import Query
from sqlalchemy.sql import select



from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import String


app = FastAPI(
    title="App"
)


# Модель данных для ввода list_values
class PredictionInput(BaseModel):
    list_values: List[Union[int, float, str]]


@app.on_event("startup")
async def startup_event():
    # Загрузка модели при старте приложения
    #load_model()
    # Запускаем фоновую задачу обновления модели
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


@app.post("/predict")
async def predict_endpoint(
        input_data: PredictionInput,
        users: Users = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    #X_train = await load_and_preprocess_data()
    #print(X_train)
    # Обновляем модель
    #train_or_update_model(X_train)

    # Сохраняем обновленную модель и переключаем её
    #save_model()
    #load_model()
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
    confirmation = prediction == [1]
    print(filtered_data)
    # Запись сессии в базу данных
    time = datetime.utcnow()
    session_data = {
        "user_id": users.id,
        "time1": str(filtered_data[2]),
        "site1": str(filtered_data[1]),
        "time2": str(filtered_data[4]),
        "site2": str(filtered_data[3]),
        "time3": str(filtered_data[6]),
        "site3": str(filtered_data[5]),
        "time4": str(filtered_data[8]),
        "site4": str(filtered_data[7]),
        "time5": str(filtered_data[10]),
        "site5": str(filtered_data[9]),
        "time6": str(filtered_data[12]),
        "site6": str(filtered_data[11]),
        "time7": str(filtered_data[14]),
        "site7": str(filtered_data[13]),
        "time8": str(filtered_data[16]),
        "site8": str(filtered_data[15]),
        "time9": str(filtered_data[18]),
        "site9": str(filtered_data[17]),
        "time10": str(filtered_data[20]),
        "site10": str(filtered_data[19]),
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
            .values(confirmation=True, target=1)
        )
        await session.execute(update_query)
        await session.commit()
        return {"message": "Сессия была обновлена и подтверждена"}

    return {"message": "Мы рады, что помогли вам"}


#@app.get("/protected-route")
#def protected_route(users: Users = Depends(current_user)):
#    return f"Hello, {users.username}"


#@app.get("/unprotected-route")
#def unprotected_route():
#    return f"Hello, anonym"