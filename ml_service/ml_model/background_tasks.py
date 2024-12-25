import asyncio
from ml_model.model import load_and_preprocess_data, train_or_update_model, save_model, switch_model

async def update_model_task():
    while True:
        # Загружаем и предобрабатываем данные
        X_train = await load_and_preprocess_data()
        # Обновляем модель
        train_or_update_model(X_train)

        # Сохраняем обновленную модель и переключаем её
        save_model()
        switch_model()  # Переключение путей после сохранения новой модели

        # Ждём 9000000 секунд перед следующим обновлением
        #print("dsdsdsdssd")
        await asyncio.sleep(90)
        #print("asasa")


async def start_update_model_task():
    #threading.Thread(target=update_model_task, daemon=True).start()
    asyncio.create_task(update_model_task())


