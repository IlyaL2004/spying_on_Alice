import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
import numpy as np
import os
from ml_model.preprocessing import preprocess_with_input

model_path_1 = "C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/model_v1.joblib"
model_path_2 = "C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/model_v2.joblib"
active_model_path = model_path_1
standby_model_path = model_path_2
model = None


def load_and_preprocess_data():
    # Загружаем и обрабатываем данные
    train_df = pd.read_csv("C:/Users/79853/Desktop/ptml/spying_on_Alice/ml_model/train_sessions.csv", index_col="session_id")
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
