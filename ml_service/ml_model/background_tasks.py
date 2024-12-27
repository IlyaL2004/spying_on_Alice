import asyncio
from ml_model.model import load_and_preprocess_data, train_or_update_model, save_model, switch_model
from payments.background_tasks_auto_payment import update_subscriptions

async def update_model_task():
    while True:
        # Загружаем и предобрабатываем данные
        X_train = await load_and_preprocess_data()
        # Обновляем модель
        train_or_update_model(X_train)

        # Сохраняем обновленную модель и переключаем её
        save_model()
        switch_model()
        await update_subscriptions()
        await asyncio.sleep(86400) #<?>


async def start_update_model_task():
    #threading.Thread(target=update_model_task, daemon=True).start()
    asyncio.create_task(update_model_task())


