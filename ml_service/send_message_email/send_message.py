import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import MY_EMAIL, MY_PASS_EMAIL

# Конфигурация SMTP сервера
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = MY_EMAIL  # Укажите вашу почту
SENDER_PASSWORD = MY_PASS_EMAIL  # Укажите пароль к вашей почте

def send_email(subject: str, body: str, email):
    try:
        # Создаём сообщение
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Подключаемся к серверу
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Шифрование соединения
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Сообщение отправлено успешно.")
    except Exception as e:
        print(f"Не удалось отправить сообщение. Ошибка: {e}")