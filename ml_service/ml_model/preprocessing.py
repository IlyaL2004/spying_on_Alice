import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier, Pool
from ml_model import config_value

def preprocess_with_input(list_values) -> csr_matrix:
    # Названия столбцов
    columns = [
        "session_id", "site1", "time1", "site2", "time2", "site3", "time3",
        "site4", "time4",  "site5", "time5", "site6", "time6", "site7", "time7",
        "site8", "time8", "site9", "time9", "site10", "time10"
    ]

    # Преобразование списка значений в DataFrame

    target_length = 21

    # Проверка текущей длины и дополнение нулями
    if len(list_values) < target_length:
        list_values.extend([0] * (target_length - len(list_values)))

    data = [list_values]
    test_df = pd.DataFrame(data, columns=columns)

    # Преобразование временных меток в формат datetime
    times = ["time%s" % i for i in range(1, 11)]
    test_df[times] = test_df[times].apply(pd.to_datetime)

    # То же самое для test_df
    test_df['day_of_week'] = test_df['time1'].dt.dayofweek
    test_df['hour'] = test_df['time1'].dt.hour
    test_df['session_duration'] = (
        (test_df[times].max(axis=1) - test_df[times].min(axis=1)).dt.total_seconds()
    )

    # Обработка сайтов
    sites = ["site%s" % i for i in range(1, 11)]
    test_df[sites] = test_df[sites].fillna(0).astype(str)

    # Преобразование сайтов в строки
    test_sites = test_df[sites].apply(lambda x: ' '.join(x), axis=1)

    # Объединение данных

    all_sites = pd.concat([config_value.train_sites, test_sites])

    # Создание векторизатора
    vectorizer = CountVectorizer()
    full_sites_sparse = vectorizer.fit_transform(all_sites)

    # Масштабирование новых признаков
    dense_features = ['day_of_week', 'hour', 'session_duration']
    full_dense_features = config_value.scaler.transform(
        test_df[dense_features])  # scaler должна браться из обучения как глобальная переменная

    # Разделение обратно на тренировочные и тестовые наборы
    idxx_split = config_value.idx_split  # эта строка должна храниться как глобальная переменная
    X_test_sparse = full_sites_sparse[idxx_split:]

    X_test_dense = full_dense_features  # может быть проблема

    # Объединение разреженных и плотных признаков

    X_test_full = hstack([X_test_sparse, csr_matrix(X_test_dense)])

    X_test_full.sort_indices()
    test_pool = Pool(X_test_full)
    return test_pool