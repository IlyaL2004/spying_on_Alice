# Проект по курсам python и ML, 5 семестр

## Тема: слежка за Алисой

### Состав команды

| ФИО | Должность |
| - | - |
| Ларин Илья Андреевич | TeamLead, BackEnd |
| Мошенский Андрей Александрович | ML |
| Коломытцева Екатерина Андреевна | ML |
| Титкова Ольга Алексеевна | BackEnd |
| Жаднов Михаил Денисович | DevOps |

### Запуск проекта

<!-- #### Подготовка

Для запуска проекта нужно в клонированном репозитории создать .env файл, поместить его в корне проекта (к docker compose файлу), прописать в нем следующие переменные:

+ DB_HOST
+ DB_PORT
+ DB_NAME
+ DB_USER
+ DB_PASS
+ YOOMONEY_CLIENT_ID
+ YOOMONEY_SECRET_KEY
+ YOOMONEY_REDIRECT_URI
+ MY_EMAIL
+ MY_PASS_EMAIL
+ SECRET_JWT
+ YOOKASSA_SHOP_ID
+ YOOKASSA_KEY

+ RABBITMQ_HOST
+ QUEUE_NAME
+ NEW_QUEUE_NAME
+ RABBITMQ_PORT
+ RABBITMQ_LOG_PORT

Также нужно предоставить обучающие данные в формате .csv, поместив их в ml_service

#### Запуск -->

+ Запустить команду `docker compose up` (если не прокатило docker compose, то заменить на docker-compose)

+ Далее ждете минуты 4-7  

+ Когда контейнер с проектом запущен, нужно перейти в контейнер ml_service, перейти в терминал и осуществить миграцию базы данных:
  + `alembic revision --autogenerate -m "COMMENT"`
  + `alembic upgrade head`
  + `psql --username=DB_USER --host=DB_HOST --dbname=DB_NAME -c "\copy start_sessions(session_id, site1, time1, site2, time2, site3, time3, site4, time4, site5, time5, site6, time6, site7, time7, site8, time8, site9, time9, site10, time10, target) FROM './train_sessions.csv' DELIMITER ',' CSV HEADER;"`, затем ввести пароль от своей бд

<!-- + После этого нужно перезапустить контейнеры с ml_service и parser_service (если позже добавим healthcheck на rabbitmq, то можно будет это вычеркнуть) -->

<!-- Теперь можно пользоваться, наверное... -->
