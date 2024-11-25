import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Конфигурация SMTP сервера
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "ilyalarin2021@gmail.com"  # Укажите вашу почту
SENDER_PASSWORD = "mzpx gvmq azvm zwrx"  # Укажите пароль к вашей почте
RECIPIENT_EMAIL = "ilalarin467@gmail.com"  # Кому отправить уведомление

def send_email(subject: str, body: str):
    try:
        # Создаём сообщение
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
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
