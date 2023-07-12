from dotenv import load_dotenv
import os

load_dotenv('.env.dev')
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
EMAIL_LOGIN = os.environ.get("EMAIL_LOGIN")
EMAIL_PASS = os.environ.get("EMAIL_PASS")
AUTH_APP_URL = os.environ.get("AUTH_APP_URL")
MANAGE_APP_URL = os.environ.get("MANAGE_APP_URL")
CLIENT_APP_URL = os.environ.get("CLIENT_APP_URL")
SECRET_KEY = os.environ.get("SECRET_KEY")
