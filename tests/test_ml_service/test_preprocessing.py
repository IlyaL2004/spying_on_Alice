import pytest
from ml_service.ml_model.preprocessing import preprocess_with_input


def test_preprocess_with_valid_data():
    data = [1, "google.com", "2023-01-01 12:00:00"] + [0] * 18
    processed_data = preprocess_with_input(data)
    assert processed_data is not None

