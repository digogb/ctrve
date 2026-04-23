from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CTRVE"
    SECRET_KEY: str = "changeme-use-env-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./ctrve.db"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_file": ".env"}


settings = Settings()
