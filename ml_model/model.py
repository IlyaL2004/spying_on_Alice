# для полного переобучения всец модели
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.linear_model import LogisticRegression

if __name__ == '__main__':
    # Чтение данных
    train_df = pd.read_csv("train_sessions.csv", index_col="session_id")

    # Преобразование временных меток
    times = ["time%s" % i for i in range(1, 11)]
    train_df[times] = train_df[times].apply(pd.to_datetime)

    # Сортировка по времени первой сессии
    train_df = train_df.sort_values(by="time1")

    for col in train_df.columns:
        if 'time' in col:
            train_df[col].fillna(train_df[col].max(), inplace=True)

    # Преобразование временных данных в числовые
    for col in train_df.columns:
        if 'time' in col:
            train_df[col] = train_df[col].astype(int) // 10 ** 9  # Преобразовать в секунды

    # Преобразование сайтов в целочисленные значения
    sites = ["site%s" % i for i in range(1, 11)]
    train_df[sites] = train_df[sites].fillna(0).astype("int")


    # Целевая переменная
    y_train = train_df["target"]
    train_df = train_df.drop("target", axis=1)



    # Обучение модели
    model = LogisticRegression(n_jobs=-1, random_state=17)
    model.fit(train_df, y_train)

    # Сохранение обученной модели в файл с использованием joblib
    joblib.dump(model, "./modell.joblib")


