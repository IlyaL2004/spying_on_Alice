from time import sleep

from sqlalchemy.connectors import asyncio

from ml_model.model import load_and_preprocess_data, train_or_update_model, save_model, switch_model
import threading

async def update_model_task():
    while True:
        # Загружаем и предобрабатываем данные
        X_train, y_train = await load_and_preprocess_data()

        # Обновляем модель
        train_or_update_model(X_train, y_train)

        # Сохраняем обновленную модель и переключаем её
        save_model()
        switch_model()  # Переключение путей после сохранения новой модели

        # Ждём 60 секунд перед следующим обновлением
        sleep(30)


async def start_update_model_task():
    #threading.Thread(target=update_model_task, daemon=True).start()
    asyncio.create_task(await update_model_task())