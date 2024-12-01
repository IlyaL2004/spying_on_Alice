import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier, Pool
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier

# Загрузка данных
trainn_df = pd.read_csv("train_sessions.csv", index_col="session_id")
test_dff = trainn_df
df = test_dff.iloc[[152]].reset_index(drop=True)
df = df[[col for col in df.columns if col != 'target']]

#test_df = pd.read_csv("test_sessions.csv", index_col="session_id")

# Преобразование временных меток в формат datetime
times = ["time%s" % i for i in range(1, 11)]
train_df[times] = train_df[times].apply(pd.to_datetime)
#test_df[times] = test_df[times].apply(pd.to_datetime)

train_df = train_df.sort_values(by="time1")

# Извлечение новых признаков из временных данных для train_df
train_df['day_of_week'] = train_df['time1'].dt.dayofweek
train_df['hour'] = train_df['time1'].dt.hour
train_df['session_duration'] = (
    (train_df[times].max(axis=1) - train_df[times].min(axis=1)).dt.total_seconds()
)

# То же самое для test_df
#test_df['day_of_week'] = test_df['time1'].dt.dayofweek
#test_df['hour'] = test_df['time1'].dt.hour
#test_df['session_duration'] = (
#    (test_df[times].max(axis=1) - test_df[times].min(axis=1)).dt.total_seconds()
#)

# Обработка сайтов
sites = ["site%s" % i for i in range(1, 11)]
train_df[sites] = train_df[sites].fillna(0).astype(str)
#test_df[sites] = test_df[sites].fillna(0).astype(str)

y_train = train_df["target"]

# Преобразование сайтов в строки
train_sites = train_df[sites].apply(lambda x: ' '.join(x), axis=1)
#test_sites = test_df[sites].apply(lambda x: ' '.join(x), axis=1)
#print(train_sites)
#print(test_sites)

# Объединение данных
all_sites = train_sites

#all_sites = pd.concat([train_sites, test_sites])

# Создание векторизатора
vectorizer = CountVectorizer()
full_sites_sparse = vectorizer.fit_transform(all_sites)

# Масштабирование новых признаков
dense_features = ['day_of_week', 'hour', 'session_duration']
scaler = StandardScaler()
full_dense_features = scaler.fit_transform(train_df[dense_features])

#full_dense_features = scaler.fit_transform(pd.concat([train_df[dense_features], test_df[dense_features]]))

# Разделение обратно на тренировочные и тестовые наборы
idx_split = train_df.shape[0] # глобальная переменная
X_train_sparse = full_sites_sparse
#X_train_sparse = full_sites_sparse[:idx_split]
#X_test_sparse = full_sites_sparse[idx_split:]

X_train_dense = full_dense_features
#X_test_dense = full_dense_features[idx_split:]

# Объединение разреженных и плотных признаков
X_train_full = hstack([X_train_sparse, csr_matrix(X_train_dense)])
#X_test_full = hstack([X_test_sparse, csr_matrix(X_test_dense)])

# Разделение данных на обучающую и валидационную выборки
#X_tr, X_val, y_tr, y_val = train_test_split(
#    X_train_full, y_train, test_size=0.1, random_state=17, stratify=y_train
#)
X_tr = X_train_full
y_tr = y_train
# Сортировка индексов разреженных матриц
X_tr.sort_indices()
#X_val.sort_indices()
#X_test_full.sort_indices()


# **2. Модель CatBoost**

# Создание объектов Pool для CatBoost без преобразования в плотный формат
train_pool = Pool(X_tr, label=y_tr)
#val_pool = Pool(X_val, label=y_val)

# Обучение модели CatBoost
catboost_model = CatBoostClassifier(
    iterations=100,
    learning_rate=0.1,
    depth=6,
    random_seed=17,
    verbose=False
)

# Обучение модели на разреженных данных
catboost_model.fit(train_pool)

# Оценка модели
#valid_pred_proba = catboost_model.predict_proba(val_pool)[:, 1]
catboost_model.save_model('model.cbm')






#train_df = pd.read_csv("train_sessions.csv", index_col="session_id")

test_df = df

# Преобразование временных меток в формат datetime
times = ["time%s" % i for i in range(1, 11)]
#train_df[times] = train_df[times].apply(pd.to_datetime)
test_df[times] = test_df[times].apply(pd.to_datetime)

#train_df = train_df.sort_values(by="time1")

# Извлечение новых признаков из временных данных для train_df
#train_df['day_of_week'] = train_df['time1'].dt.dayofweek
#train_df['hour'] = train_df['time1'].dt.hour
#train_df['session_duration'] = (
#    (train_df[times].max(axis=1) - train_df[times].min(axis=1)).dt.total_seconds()
#)

# То же самое для test_df
test_df['day_of_week'] = test_df['time1'].dt.dayofweek
test_df['hour'] = test_df['time1'].dt.hour
test_df['session_duration'] = (
    (test_df[times].max(axis=1) - test_df[times].min(axis=1)).dt.total_seconds()
)

# Обработка сайтов
sites = ["site%s" % i for i in range(1, 11)]
#train_df[sites] = train_df[sites].fillna(0).astype(str)
test_df[sites] = test_df[sites].fillna(0).astype(str)

#y_train = train_df["target"]

# Преобразование сайтов в строки
#train_sites = train_df[sites].apply(lambda x: ' '.join(x), axis=1) эьа строка запоминется и заносится в глобальную переменнею после обучения
test_sites = test_df[sites].apply(lambda x: ' '.join(x), axis=1)
#print(train_sites)
#print(test_sites)

# Объединение данных
#all_sites = train_sites

all_sites = pd.concat([train_sites, test_sites])

# Создание векторизатора
vectorizer = CountVectorizer()
full_sites_sparse = vectorizer.fit_transform(all_sites)

# Масштабирование новых признаков
dense_features = ['day_of_week', 'hour', 'session_duration']
#scaler = StandardScaler()
#full_dense_features = scaler.fit_transform(train_df[dense_features])
full_dense_features = scaler.transform(test_df[dense_features]) # scaler должна браться из обучения как глобальная переменная
#full_dense_features = scaler.fit_transform(pd.concat([train_df[dense_features], test_df[dense_features]]))

# Разделение обратно на тренировочные и тестовые наборы
idxx_split = idx_split # эта строка должна храниться как глобальная переменная
#X_train_sparse = full_sites_sparse
#X_train_sparse = full_sites_sparse[:idx_split]
X_test_sparse = full_sites_sparse[idxx_split:]

#X_train_dense = full_dense_features
X_test_dense = full_dense_features# может быть проблема

# Объединение разреженных и плотных признаков
#X_train_full = hstack([X_train_sparse, csr_matrix(X_train_dense)])
X_test_full = hstack([X_test_sparse, csr_matrix(X_test_dense)])



#
# Масштабирование новых признаков
#full_dense_features = scaler.transform(test_df[dense_features])  # Используйте transform
#X_test_sparse = full_sites_sparse[idx_split:]
#X_test_dense = csr_matrix(full_dense_features)  # Преобразование в разреженную матрицу

# Объединение разреженных и плотных признаков
#X_test_full = hstack([X_test_sparse, X_test_dense])
#X_test_full.sort_indices()
#




# Разделение данных на обучающую и валидационную выборки
#X_tr, X_val, y_tr, y_val = train_test_split(
#    X_train_full, y_train, test_size=0.1, random_state=17, stratify=y_train
#)
#X_tr = X_train_full
#y_tr = y_train
# Сортировка индексов разреженных матриц
#X_tr.sort_indices()
#X_val.sort_indices()
X_test_full.sort_indices()


# **2. Модель CatBoost**

# Создание объектов Pool для CatBoost без преобразования в плотный формат
#train_pool = Pool(X_tr, label=y_tr)
#val_pool = Pool(X_val, label=y_val)

# Обучение модели CatBoost
#catboost_model = CatBoostClassifier(
#    iterations=100,
#    learning_rate=0.1,
#    depth=6,
#    random_seed=17,
#    verbose=False
#)

# Обучение модели на разреженных данных
#catboost_model.fit(train_pool)

# Оценка модели


loaded_model = CatBoostClassifier()
loaded_model.load_model('model.cbm')

test_pool = Pool(X_test_full)
test_pred_catboost = loaded_model.predict_proba(test_pool)[:, 1]
test_pred = test_pred_catboost[0]
print(test_pred)
if test_pred > 0.006:
  print(1)
else:
  print(0)