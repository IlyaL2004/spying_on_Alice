from pydantic import BaseModel
from typing import List, Union
from send_message_email.send_message import send_email
from ml_model.model import get_model_prediction_with_input
from sqlalchemy import insert
from models.models import sessions
from fastapi import APIRouter, Depends, HTTPException
from auth.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

class PredictionInput(BaseModel):
    list_values: List[Union[int, float, str]]

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
    print(confirmation)
    # Отправка уведомления при предсказании 0
    if not confirmation:
        subject = "Model Alert"
        body = f"На вашем аккаунте выполнены подозрительные действия. Вам следует сменить пароль. Помогите нам лучше распознавать подозрительные действия, перейдите по сыслке ""http://127.0.0.1:8000/docs#/default/check_session_check_session_get"" введите свою почту, это время " + str(time) + " и если вы согласны с предсказание введидте да, если не согласны, то введите нет"
        send_email(subject, body, email)

    return {"predictions": prediction}
