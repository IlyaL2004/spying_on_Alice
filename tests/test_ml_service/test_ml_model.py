import pytest
from ml_service.ml_model.model import predict

def test_predict_suspicious():
    data = {"list_values": [153, 5397, "2013-11-22 13:23:49", 5395.0, ...]}
    result = predict(data)
    assert result == 1  # Проверяем, что предсказание подозрительное

def test_predict_non_suspicious():
    data = {"list_values": [12, 30, "2023-01-01 12:00:00", 5.0, ...]}
    result = predict(data)
    assert result == 0

