
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    FACEBOOK_ACCESS_TOKEN: str
    FACEBOOK_PAGE_ID: str

    MASTODON_BASE_URL: str
    MASTODON_ACCESS_TOKEN: str

    BLUESKY_HANDLE: str
    BLUESKY_APP_PASSWORD: str

    DEVTO_API_KEY: str

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHANNEL_ID: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
