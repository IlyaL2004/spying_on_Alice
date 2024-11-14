from flask import Flask, request, make_response, jsonify
from datetime import datetime
import uuid
import json
import os

app = Flask(__name__)

# Список эмулируемых сайтов
SITES = [f"site_{i}" for i in range(1, 16)]

# Путь к файлу с данными
DATA_FILE = 'visits.json'


def load_visits():
    """Загрузка данных о посещениях из файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_visits(visits):
    """Сохранение данных о посещениях в файл"""
    with open(DATA_FILE, 'w') as f:
        json.dump(visits, f)


def get_user_id(request):
    """Получение или создание ID пользователя"""
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
    return user_id


@app.route('/<site_name>')
def visit_site(site_name):
    """Обработка посещения сайта"""
    if site_name not in SITES:
        return "Site not found", 404

    user_id = get_user_id(request)
    timestamp = datetime.now().isoformat()

    visits = load_visits()

    if user_id not in visits:
        visits[user_id] = []

    # Добавляем новое посещение
    visits[user_id].insert(0, {
        'site': site_name,
        'timestamp': timestamp
    })

    # Оставляем только последние 100 посещений
    visits[user_id] = visits[user_id][:100]

    save_visits(visits)

    response = make_response(f"Visiting {site_name}")
    response.set_cookie('user_id', user_id)
    return response


@app.route('/history')
def get_history():
    """Получение последних 5 посещенных сайтов"""
    user_id = get_user_id(request)
    visits = load_visits()

    user_visits = visits.get(user_id, [])
    return jsonify(user_visits[:5])


if __name__ == '__main__':
    app.run(debug=True)
