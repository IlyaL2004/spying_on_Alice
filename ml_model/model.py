import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
import numpy as np
import os
from ml_model.preprocessing import preprocess_with_input
import pandas as pd
from sqlalchemy import create_engine, text
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
import pandas as pd

model_path_1 = "C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/model_v1.joblib"
model_path_2 = "C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/model_v2.joblib"
active_model_path = model_path_1
standby_model_path = model_path_2
model = None


async def load_data_bd():
    # Асинхронное подключение к базе данных (замените на ваши параметры)
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Создание асинхронного движка
    engine = create_async_engine(DATABASE_URL)

    # SQL-запрос для извлечения данных
    query = text("""
    SELECT session_id, time1, site1, time2, site2, time3, site3, 
           time4, site4, time5, site5, time6, site6, 
           time7, site7, time8, site8, time9, site9, 
           time10, site10, target
    FROM sessions
    WHERE confirmation = TRUE
    """)
    async with engine.connect() as connection:
        result = await connection.execute(query)
        # Преобразуем результат в DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df

async def load_and_preprocess_data():


    train_df = await load_data_bd()
    print(train_df.head())  # Пример вывода для проверки


    #train_df = pd.read_csv("C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/train_sessions.csv", index_col="session_id")
    times = ["time%s" % i for i in range(1, 11)]
    train_df[times] = train_df[times].apply(pd.to_datetime)
    train_df = train_df.sort_values(by="time1")

    for col in train_df.columns:
        if 'time' in col:
            train_df[col] = train_df[col].fillna(train_df[col].max())

    for col in train_df.columns:
        if 'time' in col:
            train_df[col] = train_df[col].astype(int) // 10 ** 9

    sites = ["site%s" % i for i in range(1, 11)]
    train_df[sites] = train_df[sites].fillna(0).astype("int")

    y_train = train_df["target"]
    train_df = train_df.drop("target", axis=1)

    return train_df, y_train


def train_or_update_model(X_train, y_train):
    global model
    if model is None:
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
    else:
        model.fit(X_train, y_train)
    return model


def save_model():
    joblib.dump(model, standby_model_path)


def switch_model():
    global active_model_path, standby_model_path
    active_model_path, standby_model_path = standby_model_path, active_model_path
    load_model()  # Перезагружаем модель из нового активного файла


def load_model():
    global model
    if os.path.exists(active_model_path):
        model = joblib.load(active_model_path)


def get_model_prediction_with_input(list_values):
    if model:
        features_sparse = preprocess_with_input(list_values)
        return model.predict(features_sparse).tolist()
    else:
        return "Model is not yet loaded."
