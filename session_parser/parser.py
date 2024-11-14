# def session_data():
#     list_values = [
#         2, 890, "2014-02-22 11:19:50", 941.0, "2014-02-22 11:19:50", 3847.0,
#         "2014-02-22 11:19:51", 941.0, "2014-02-22 11:19:51", 942.0,
#         "2014-02-22 11:19:51", 3846.0, "2014-02-22 11:19:51", 3847.0,
#         "2014-02-22 11:19:52", 3846.0, "2014-02-22 11:19:52", 1516.0,
#         "2014-02-22 11:20:15", 1518.0, "2014-02-22 11:20:16"
#     ]
#
#     list_values = [
#         153, 5397, "2013-11-22 13:23:49", 5395.0, "2013-11-22 13:23:49",
#     22.0, "2013-11-22 13:23:50", 5396.0, "2013-11-22 13:23:50", 5402.0, "2013-11-22 13:23:50",
#     5392.0, "2013-11-22 13:23:50", 22.0, "2013-11-22 13:23:51", 35.0, "2013-11-22 13:23:54",
#     33.0, "2013-11-22 13:23:54", 338.0, "2013-11-22 13:23:54"
#     ]
#     return list_values

import json
from datetime import datetime, timedelta

class VisitsParser:
    def __init__(self, file_path='visits.json'):
        self.file_path = file_path
        self.visits_data = self.load_data()

    def load_data(self):
        """Загрузка данных из JSON файла"""
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Ошибка: Файл {self.file_path} не найден")
            return {}
        except json.JSONDecodeError:
            print(f"Ошибка: Файл {self.file_path} содержит некорректный JSON")
            return {}

    def get_recent_visits(self, user_id, limit=10, time_window=30):
        """Получение последних посещений за последние time_window минут"""
        if user_id not in self.visits_data:
            print(f"Пользователь с ID {user_id} не найден")
            return []

        now = datetime.now()
        time_threshold = now - timedelta(minutes=time_window)

        # Фильтруем посещения по времени
        recent_visits = [
            visit for visit in self.visits_data[user_id]
            if datetime.fromisoformat(visit['timestamp']) >= time_threshold
        ]

        return recent_visits[:limit]

def session_data(user_id, limit=5):
    """Функция для получения данных о посещениях пользователя"""
    visits_parser = VisitsParser()
    visits = visits_parser.get_recent_visits(user_id)

    # Преобразование данных в нужный формат
    list_values = [user_id]
    for visit in visits:
        timestamp = datetime.fromisoformat(visit['timestamp'])
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        list_values.append(visit['site'])
        list_values.append(formatted_time)

    return list_values

# if __name__ == "__main__":
#     user_id = "1ac4433b-ef30-4175-99b4-731cc4792fc2"
#     data = session_data(user_id)
#     print(data)
