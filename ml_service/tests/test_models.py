import unittest
from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from datetime import datetime
from models.models import users, sessions, start_sessions  # импорт ваших таблиц

class TestDatabaseModels(unittest.TestCase):
    def assertTableEquals(self, table, expected_columns, expected_primary_key):
        columns = {col.name: col for col in table.columns}
        self.assertEqual(set(columns.keys()), set(expected_columns))  # Проверяем имена столбцов
        # Проверяем типы данных столбцов
        for col_name in expected_columns:
            self.assertEqual(type(columns[col_name].type), type(expected_columns[col_name]))
        self.assertEqual(tuple(table.primary_key), tuple(expected_primary_key))

    def test_users_table(self):
        expected_columns = {
            "id": Integer(),
            "email": String(),
            "username": String(),
            "hashed_password": String(),
            "registered_at": TIMESTAMP(),
            "is_active": Boolean(),
            "is_superuser": Boolean(),
            "is_verified": Boolean(),
            "subscription_end": TIMESTAMP(),
            "payment_id": String(),
            "payment_confirmation": Boolean(),
        }

        expected_primary_key = (users.c.id,)
        self.assertTableEquals(users, expected_columns, expected_primary_key)

    def test_sessions_table(self):
        expected_columns = {
            "session_id": Integer(),
            "user_id": Integer(),
            "time1": String(),
            "site1": String(),
            "time2": String(),
            "site2": String(),
            "time3": String(),
            "site3": String(),
            "time4": String(),
            "site4": String(),
            "time5": String(),
            "site5": String(),
            "time6": String(),
            "site6": String(),
            "time7": String(),
            "site7": String(),
            "time8": String(),
            "site8": String(),
            "time9": String(),
            "site9": String(),
            "time10": String(),
            "site10": String(),
            "email": String(),
            "target": Integer(),
            "confirmation": Boolean(),
            "date": TIMESTAMP(),
        }
        expected_primary_key = (sessions.c.session_id,)
        self.assertTableEquals(sessions, expected_columns, expected_primary_key)

    def test_start_sessions_table(self):
        expected_columns = {
            "session_id": Integer(),
            "site1": String(),
            "time1": String(),
            "site2": String(),
            "time2": String(),
            "site3": String(),
            "time3": String(),
            "site4": String(),
            "time4": String(),
            "site5": String(),
            "time5": String(),
            "site6": String(),
            "time6": String(),
            "site7": String(),
            "time7": String(),
            "site8": String(),
            "time8": String(),
            "site9": String(),
            "time9": String(),
            "site10": String(),
            "time10": String(),
            "target": Integer(),
        }
        expected_primary_key = (start_sessions.c.session_id,)
        self.assertTableEquals(start_sessions, expected_columns, expected_primary_key)

if __name__ == "__main__":
    unittest.main()
