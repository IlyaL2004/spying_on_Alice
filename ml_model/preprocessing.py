import pandas as pd
from scipy.sparse import csr_matrix

def preprocess_with_input(list_values) -> csr_matrix:
    # Названия столбцов
    columns = [
        "session_id", "site1", "time1", "site2", "time2", "site3", "time3",
        "site4", "time4",  "site5", "time5", "site6", "time6", "site7", "time7",
        "site8", "time8", "site9", "time9", "site10", "time10"
    ]

    # Преобразование списка значений в DataFrame
    data = [list_values]
    test_df = pd.DataFrame(data, columns=columns)

    # Преобразование временных меток
    time_columns = [col for col in columns if "time" in col]
    for col in time_columns:
        test_df[col] = pd.to_datetime(test_df[col], errors="coerce").fillna(0).astype(int) // 10 ** 9

    # Преобразование сайтов в целочисленные значения
    sites = ["site%s" % i for i in range(1, 11)]
    test_df[sites] = test_df[sites].fillna(0).astype("int")

    return csr_matrix(test_df.drop(columns=["session_id"]))
