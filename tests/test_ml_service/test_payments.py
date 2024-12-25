from unittest.mock import patch
from ml_service.payments.pay import process_payment

def test_payment_success():
    with patch("ml_service.payments.gateway.charge_card") as mock_charge:
        mock_charge.return_value = {"status": "success"}
        result = process_payment(user_id=1, amount=100.0)
        assert result["status"] == "success"

def test_payment_failure():
    with patch("ml_service.payments.gateway.charge_card") as mock_charge:
        mock_charge.return_value = {"status": "failure"}
        result = process_payment(user_id=1, amount=100.0)
        assert result["status"] == "failure"

