from fastapi_users import FastAPIUsers
from auth.auth import auth_backend
from auth.menager import get_user_manager
from send_message_email.send_message import send_email
from fastapi import FastAPI, Query, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.types import String
from sqlalchemy.future import select
from ml_model.model import get_model_prediction_with_input
from sqlalchemy import insert
from models.models import sessions
from fastapi import APIRouter, Depends, HTTPException
from auth.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from auth.database import Users
from datetime import datetime
from pydantic import BaseModel
from typing import List, Union

#from main import PredictionInput


class PredictionInput(BaseModel):
    list_values: List[Union[int, float, str]]

predict_and_confirmation_router = APIRouter()

fastapi_users = FastAPIUsers[Users, int](
    get_user_manager,
    [auth_backend],
)



current_user = fastapi_users.current_user()

print(current_user)

@predict_and_confirmation_router.post("/predict")
async def predict_endpoint(
        input_data: PredictionInput,
        users: Users = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    print(users)
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
    print(confirmation)
    if not confirmation:
        subject = "Model Alert"
        body = f"На вашем аккаунте выполнены подозрительные действия. Вам следует сменить пароль. Помогите нам лучше распознавать подозрительные действия, перейдите по сыслке ""http://127.0.0.1:8000/docs#/default/check_session_check_session_get"" введите свою почту, это время " + str(time) + " и если вы согласны с предсказание введидте да, если не согласны, то введите нет"
        send_email(subject, body, email)

    return {"predictions": prediction}




@predict_and_confirmation_router.get("/check-session")
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





