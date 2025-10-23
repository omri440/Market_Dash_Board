from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    IBKR_DEFAULT_HOST: str = "127.0.0.1"
    IBKR_DEFAULT_PORT: int = 7497
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


settings = Settings()