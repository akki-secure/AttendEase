from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/attend_ease.db"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8時間

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    OTP_EXPIRE_MINUTES: int = 10
    OTP_RESEND_INTERVAL_SECONDS: int = 60

    DEV_OTP_BYPASS: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
