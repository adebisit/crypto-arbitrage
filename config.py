from pydantic import BaseSettings, EmailStr
from fastapi_mail import FastMail, ConnectionConfig
from jinja2 import FileSystemLoader, Environment


class Settings(BaseSettings):
    ATLAS_URI: str
    DB_NAME: str
    JWT_SECRET: str
    MAIL_HOST: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr

    class Config:
        env_file = ".env"
    
settings = Settings()

conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = settings.MAIL_PASSWORD,
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_SERVER = settings.MAIL_HOST,
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS=True
)

fastmail = FastMail(conf)
mail_env = Environment(loader=FileSystemLoader('app/templates'))