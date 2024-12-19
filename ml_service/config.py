from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
YOOMONEY_REDIRECT_URI = os.environ.get("YOOMONEY_REDIRECT_URI")
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_PASS_EMAIL = os.environ.get("MY_PASS_EMAIL")
SECRET_JWT = os.environ.get("SECRET_JWT")
YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID")
YOOKASSA_KEY = os.environ.get("YOOKASSA_KEY")