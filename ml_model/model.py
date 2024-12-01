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
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier, Pool


model_path_1 = "C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/model_v1.cbm"
model_path_2 = "C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/model_v2.cbm"
active_model_path = model_path_1
standby_model_path = model_path_2
model = None
train_sites = None
scaler = None
idx_split = None


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
    UNION ALL
    SELECT session_id, time1, site1, time2, site2, time3, site3, 
           time4, site4, time5, site5, time6, site6, 
           time7, site7, time8, site8, time9, site9, 
           time10, site10, target
    FROM start_sessions;
    """)
    async with engine.connect() as connection:
        result = await connection.execute(query)
        # Преобразуем результат в DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df




async def load_and_preprocess_data():


    train_df = await load_data_bd()
    train_df.set_index('session_id', inplace=True)
    #train_df = pd.read_csv("C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/train_sessions.csv", index_col="session_id")

    times = ["time%s" % i for i in range(1, 11)]

    train_df[times] = train_df[times].apply(pd.to_datetime)
    #print(train_df)
    train_df = train_df.sort_values(by="time1")

    # Извлечение новых признаков из временных данных для train_df
    train_df['day_of_week'] = train_df['time1'].dt.dayofweek
    train_df['hour'] = train_df['time1'].dt.hour
    train_df['session_duration'] = (
        (train_df[times].max(axis=1) - train_df[times].min(axis=1)).dt.total_seconds()
    )
    sites = ["site%s" % i for i in range(1, 11)]
    train_df[sites] = train_df[sites].fillna(0).astype(str)
    y_train = train_df["target"]
    global train_sites
    train_sites = train_df[sites].apply(lambda x: ' '.join(x), axis=1) #ьа строка запоминется и заносится в глобальную переменнею после обучения

    all_sites = train_sites


    # Создание векторизатора
    vectorizer = CountVectorizer()
    full_sites_sparse = vectorizer.fit_transform(all_sites)

    # Масштабирование новых признаков
    dense_features = ['day_of_week', 'hour', 'session_duration']
    global scaler
    scaler = StandardScaler()
    full_dense_features = scaler.fit_transform(train_df[dense_features]) # scaler должна браться из обучения как глобальная переменная
    global idx_split
    idx_split = train_df.shape[0]  # глобальная переменная
    X_train_sparse = full_sites_sparse

    X_train_dense = full_dense_features

    # Объединение разреженных и плотных признаков
    X_train_full = hstack([X_train_sparse, csr_matrix(X_train_dense)])
    X_tr = X_train_full
    y_tr = y_train
    # Сортировка индексов разреженных матриц
    X_tr.sort_indices()

    # Создание объектов Pool для CatBoost без преобразования в плотный формат
    train_pool = Pool(X_tr, label=y_tr)
    return train_pool

def train_or_update_model(X_train):
    global model
    print(X_train)
    print(f"X_train shape: {X_train.shape}")
    if model is None:
        model = CatBoostClassifier(
            iterations=100,
            learning_rate=0.1,
            depth=6,
            random_seed=17,
            verbose=False
        )
        model.fit(X_train)
    else:
        model.fit(X_train)
    print(1)
    return model


def save_model():
    #joblib.dump(model, standby_model_path)
    model.save_model(standby_model_path)


def switch_model():
    global active_model_path, standby_model_path
    active_model_path, standby_model_path = standby_model_path, active_model_path
    load_model()  # Перезагружаем модель из нового активного файла


def load_model():
    global model
    if os.path.exists(active_model_path):
        #model = joblib.load(active_model_path)
         model.load_model(active_model_path)


def get_model_prediction_with_input(list_values):
    if model:
        features_sparse = preprocess_with_input(list_values)
        pred_catboost = model.predict_proba(features_sparse)[:, 1]
        test_pred = pred_catboost[0]
        print(test_pred)
        if test_pred > 0.006:
            return 1
        else:
            return 0
    else:
        return "Model is not yet loaded."
