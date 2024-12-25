import os
from ml_model.preprocessing import preprocess_with_input
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
from scipy.sparse import csr_matrix, hstack
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier, Pool

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
import pandas as pd
from models.models import sessions
from models.models import start_sessions
from ml_model import config_value

# Определение базы данных
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание асинхронного движка и сессии
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

#model = None



async def load_data_bd():
    async with AsyncSessionLocal() as session:
        query = (
            select(
                sessions.c.session_id, sessions.c.time1, sessions.c.site1, sessions.c.time2, sessions.c.site2,
                sessions.c.time3, sessions.c.site3, sessions.c.time4, sessions.c.site4,
                sessions.c.time5, sessions.c.site5, sessions.c.time6, sessions.c.site6,
                sessions.c.time7, sessions.c.site7, sessions.c.time8, sessions.c.site8,
                sessions.c.time9, sessions.c.site9, sessions.c.time10, sessions.c.site10,
                sessions.c.target
            )
            .where(sessions.c.confirmation == True)
            .union_all(
                select(
                    start_sessions.c.session_id, start_sessions.c.time1, start_sessions.c.site1,
                    start_sessions.c.time2, start_sessions.c.site2, start_sessions.c.time3,
                    start_sessions.c.site3, start_sessions.c.time4, start_sessions.c.site4,
                    start_sessions.c.time5, start_sessions.c.site5, start_sessions.c.time6,
                    start_sessions.c.site6, start_sessions.c.time7, start_sessions.c.site7,
                    start_sessions.c.time8, start_sessions.c.site8, start_sessions.c.time9,
                    start_sessions.c.site9, start_sessions.c.time10, start_sessions.c.site10,
                    start_sessions.c.target
                )
            )
        )

        result = await session.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        print(f"X_train shape: {df.shape}")
        return df


async def load_and_preprocess_data():

    train_df = await load_data_bd()
    train_df.set_index('session_id', inplace=True)

    times = ["time%s" % i for i in range(1, 11)]

    train_df[times] = train_df[times].apply(pd.to_datetime)
    train_df = train_df.sort_values(by="time1")

    train_df['day_of_week'] = train_df['time1'].dt.dayofweek
    train_df['hour'] = train_df['time1'].dt.hour
    train_df['session_duration'] = (
        (train_df[times].max(axis=1) - train_df[times].min(axis=1)).dt.total_seconds()
    )
    sites = ["site%s" % i for i in range(1, 11)]
    train_df[sites] = train_df[sites].fillna(0).astype(str)
    y_train = train_df["target"]
    #global train_sites
    train_sites = train_df[sites].apply(lambda x: ' '.join(x), axis=1)
    config_value.train_sites = train_sites
    all_sites = train_sites

    vectorizer = CountVectorizer()
    full_sites_sparse = vectorizer.fit_transform(all_sites)

    dense_features = ['day_of_week', 'hour', 'session_duration']
    scaler = StandardScaler()
    full_dense_features = scaler.fit_transform(train_df[dense_features])
    config_value.scaler = scaler
    idx_split = train_df.shape[0]  # глобальная переменная
    config_value.idx_split = idx_split
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
    print(X_train)
    print(f"X_train shape: {X_train.shape}")
    if config_value.model is None:
        config_value.model = CatBoostClassifier(
            iterations=100,
            learning_rate=0.1,
            depth=6,
            random_seed=17,
            verbose=False
        )
        config_value.model.fit(X_train)
    else:
        config_value.model.fit(X_train)
    #return model

def save_model():
    config_value.model.save_model(config_value.standby_model_path)

def switch_model():
    config_value.active_model_path, config_value.standby_model_path = config_value.standby_model_path, config_value.active_model_path
    load_model()  # Перезагружаем модель из нового активного файла

def load_model():
    if os.path.exists(config_value.active_model_path):
         config_value.model.load_model(config_value.active_model_path)

def get_model_prediction_with_input(list_values):
    if config_value.model:
        features_sparse = preprocess_with_input(list_values)
        pred_catboost = config_value.model.predict_proba(features_sparse)[:, 1]
        test_pred = pred_catboost[0]
        print(test_pred)
        if test_pred > 0.006:
            return 1
        else:
            return 0
    else:
        return "Model is not yet loaded."
