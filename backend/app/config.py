from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_expire_minutes: int = Field(default=1440, alias="JWT_EXPIRE_MINUTES")
    admin_email: str = Field(alias="ADMIN_EMAIL")
    admin_password: str = Field(alias="ADMIN_PASSWORD")
    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    bot_daily_hour: int = Field(default=9, alias="BOT_DAILY_HOUR")
    next_public_api_url: str | None = Field(default=None, alias="NEXT_PUBLIC_API_URL")
    bot_internal_token: str | None = Field(default=None, alias="BOT_INTERNAL_TOKEN")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
