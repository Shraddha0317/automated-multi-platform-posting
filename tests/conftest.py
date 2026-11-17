
import pytest

from app.config import Settings


@pytest.fixture
def settings():
    return Settings(
        FACEBOOK_ACCESS_TOKEN="test-facebook-token",
        FACEBOOK_PAGE_ID="123456789",
        MASTODON_BASE_URL="https://mastodon.social",
        MASTODON_ACCESS_TOKEN="test-mastodon-token",
        BLUESKY_HANDLE="test.example.com",
        BLUESKY_APP_PASSWORD="test-app-password",
        DEVTO_API_KEY="test-devto-key",
        TELEGRAM_BOT_TOKEN="test-telegram-token",
        TELEGRAM_CHANNEL_ID="@testchannel"
    )
