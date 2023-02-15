from pydantic import BaseSettings

class Settings(BaseSettings):
    ATLAS_URI: str
    DB_NAME: str
    JWT_SECRET: str

    class Config:
        env_file = ".env"

settings = Settings()