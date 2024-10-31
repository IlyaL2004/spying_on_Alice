import joblib
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.linear_model import LogisticRegression
from session_parser import parser

def preprocess() -> csr_matrix:

    list_values = parser.session_data()

    # Названия столбцов
    columns = [
        "session_id", "site1", "time1", "site2", "time2", "site3", "time3",
        "site4", "time4",  "site5", "time5", "site6", "time6", "site7", "time7",
        "site8", "time8", "site9", "time9", "site10", "time10"
    ]

    # Преобразование списка значений в DataFrame
    data = [list_values]  # оборачиваем values в список, чтобы создать одну строку
    test_df = pd.DataFrame(data, columns=columns)

    # Преобразование строковых дат в формат datetime для временных столбцов
    time_columns = [col for col in columns if "time" in col]
    for col in time_columns:
        test_df[col] = pd.to_datetime(test_df[col])

    test_df = test_df.drop(columns=['session_id'])

    # Преобразование временных меток
    times = ["time%s" % i for i in range(1, 11)]
    test_df[times] = test_df[times].apply(pd.to_datetime)

    # Сортировка по времени первой сессии
    test_df = test_df.sort_values(by="time1")

    for col in test_df.columns:
        if 'time' in col:
            test_df[col].fillna(test_df[col].max(), inplace=True)

        # Преобразование временных данных в числовые
    for col in test_df.columns:
        if 'time' in col:
            test_df[col] = test_df[col].astype(int) // 10 ** 9  # Преобразовать в секунды

    # Преобразование сайтов в целочисленные значения
    sites = ["site%s" % i for i in range(1, 11)]
    test_df[sites] = test_df[sites].fillna(0).astype("int")


    # Объединение данных для обработки
    full_df = test_df

    return full_df


