import unittest
from fastapi_users.authentication.strategy import JWTStrategy

class TestAuthModule(unittest.TestCase):
    def test_jwt_strategy_secret_length(self):
        # Provide lifetime_seconds
        strategy = JWTStrategy(secret="a_very_long_secret_key_for_testing", lifetime_seconds=3600)  # 3600 seconds = 1 hour
        self.assertTrue(len(strategy.secret) >= 32)

if __name__ == "__main__":
    unittest.main()
