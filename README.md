Туториал по запуску программы. Вся тягость без докера.
Каждая папка является сервисом. google_sites и yandex_sites - это отдельные серверы для парсинга данных.
parser_service и ml_service - это два наших микосервиса, нашего сервиса по выявлению мошеннической деятельности.
google_sites и yandex_sites передают json деятельности свих пользователей. parser_service получает эти json по очереди rerbbitmq.
parser_service обрапатывает данные, которые будут удобны для предсказания. Потом мы эти спаршенные данные передаём ml_service.
ml_service принимает эти данные и делает прогноз. Также в ml_service реализована авторизаия, регистраия, платежи.
1. Клонируем репу и переходим в ветку back_with_microservices
2. Создаём 4 терминала для каждой папки.
3. Запускаем отдельно в другом терминале базу данных "docker run --name alice -p 5432:5432 -e POSTGRES_USER=alice -e POSTGRES_PASSWORD=alice -e POSTGRES_DB=alice -d postgres:13.3"
4. Запускаем отдельно RabbitMQ "docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management"
5. Создаем окужение для каждого сервиса. Для этого в каждом терминале, каждому из которых соответствует одна папка. Вводим команды  "python -m venv venv", "venv\Scripts\activate", "pip install -r requirements.txt".
6. У нас есть миграции alembic в ml_service, которые определяют схему нашей базы данных. Нам нужно зайти в терминал, который соответствует ml_service и ввести команду "alembic upgrade head".
7. Теперь в наш контейнер с бд перенесём csv файл откроем терминале с бд прописываем команду "docker cp C:\Users\79853\Desktop\train_sessions.csv dcf65414811a:/home/train_sessions.csv" (пояснение кавычек: "C:\Users\79853\Desktop\train_sessions.csv" - место, где храниться csv на вашем компьютере. dcf65414811a:/home/train_sessions.csv здесь нужно поменять только название вашего поднятого контейнера с докером)
8. Теперь нужно перекопировать csv файл в нашу пустую таблицу в базе данных. Нужно ввести в терминал из 7 пункта "docker exec -it dcf65414811a psql -U alice -d alice -c "\copy start_sessions(session_id, site1, time1, site2, time2, site3, time3, site4, time4, site5, time5, site6, time6, site7, time7, site8, time8, site9, time9, site10, time10, target) FROM '/home/train_sessions.csv' DELIMITER ',' CSV HEADER;"" (в этой строке опять нужно поменять название на название контейнера своего с базой данных)
9. Запускаем в каждом терминале, каждому из которых соответствует одна папка. Для google_sites выводим "python site.py", для yandex_sites вводи "python site1.py", для parser_service вводим uvicorn main:app --reload --port 8001, для ml_service вводим uvicorn main:app --reload.
Работаем с запущенной порогой.
10. В ml_service в файле .env замените на свои значения. MY_EMAIL="ilyalarin2021@gmail.com", MY_PASS_EMAIL="hbmd ehql qkxp oenn". Для получения MY_PASS_EMAIL, найдите в гугле страницу пароли приложений и сгенериуйте пароль для вашей почты. Для генерации пароля нужно, чтобы аккаунт имел двухфакторную аунтификацию. Если её нет, то нужно настроить. MY_EMAIL сюда вставьте свою почту в котрой вы генерили пароль.
1. Мы должны заегестироваться. Для пользователя с id 1, то есть первого в бд. Будет всё бесплатно. Для следующих пользователей зарегестрированных нужно будет залогинеться и оплать подписку (выйдёт ссылка при нажитии на соответствующую кнопку в свагере, нужно будет оплатить и полтом нажать на другую кнопку в свагере с подтвеждением, что ты оплатил, тогда вы будете иметь доступ к предсказаниям)
2. Есть кнопка предикт, куда вы можете вставить свою строку типа "{
  "list_values": ["ilyalarin2021@gmail.com", 153, 5397, "2013-11-22 13:23:49", 5395.0, "2013-11-22 13:23:49", 
  22.0, "2013-11-22 13:23:50", 5396.0, "2013-11-22 13:23:50", 5402.0, "2013-11-22 13:23:50",
  5392.0, "2013-11-22 13:23:50", 22.0, "2013-11-22 13:23:51", 35.0, "2013-11-22 13:23:54",
  33.0, "2013-11-22 13:23:54", 338.0, "2013-11-22 13:23:54"]
}"
Мне прийдёт на почту сообщение о подозрительных действиях. Так как модель дост предикт 1, соответствующий подозрительным действиям. Для 0 на почту ничего не отправляется. Можете поменять в этой строке на свою почту и вам прийдёт уведомление. В этом сообщении будет ссылка по которой вы должны перейти. Ввести тебуемые данные из сообщения в свагер, тем самым вы улучшите мл модель.
3. Мы можем чтобы строка парсилась за нас и мы предикт не ждали. Для этого введите "http://127.0.0.1:5000/admin1/5" и поперезагужайте страницы, меняя значение от 1 до 16. В ml_service минут через 1.5 в терминале вы увидете предсказание.
4. Однако собщение не отправится. Так как при перезапуске компьютера uuid меняется. 
Сейчас нужно поработать с терминалами и соответвующими им директориями в google_sites и в yandex_sites в файле main. Для этого замените первое значение в словаре uuid, которое вам выпадет в терминале. И соответсвующую своую электронную почту. USER_EMAILS = {
    "ac6d5844-f8c7-4715-91ab-a628c8462c70": "ilyalarin2021@gmail.com",
    "67a86189-eede-4d71-8166-07db226ac145": "ilalarin467@gmail.com",
} (начинается с 39 строки main).
5. Теперь опять можете вернуться к 3 пункту и теперь вы точно увидете предсказание в терминале ml_service.
