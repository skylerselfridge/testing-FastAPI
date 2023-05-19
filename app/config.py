from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_HOSTNAME: str
    DB_PORT: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_USERNAME: str
    TEST_DB_NAME: str
    SECRET_KEY: str
    TOKEN_ALGORITHM: str
    TOKEN_EXPIRE: int

    class Config:
        env_file = ".env"


settings = Settings()
