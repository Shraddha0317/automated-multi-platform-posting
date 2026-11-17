from unittest.mock import AsyncMock, patch

from app.platforms.base import PublishResult
from app.platforms.facebook import FacebookPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.telegram import TelegramPlatform
from app.services.posting_service import publish_to_all


async def test_publish_to_all_returns_five_results(settings):

    with (
        patch.object(FacebookPlatform, "publish", new_callable=AsyncMock) as mock_fb,
        patch.object(MastodonPlatform, "publish", new_callable=AsyncMock) as mock_mastodon,
        patch.object(BlueskyPlatform, "publish", new_callable=AsyncMock) as mock_bsky,
        patch.object(DevToPlatform, "publish", new_callable=AsyncMock) as mock_devto,
        patch.object(TelegramPlatform, "publish", new_callable=AsyncMock) as mock_telegram
    ):
        mock_fb.return_value = PublishResult(platform="facebook", status="success")
        mock_mastodon.return_value = PublishResult(platform="mastodon", status="success")
        mock_bsky.return_value = PublishResult(platform="bluesky", status="success")
        mock_devto.return_value = PublishResult(platform="devto", status="success")
        mock_telegram.return_value = PublishResult(platform="telegram", status="success")

        results = await publish_to_all(
            "Test message https://example.com", "https://example.com", settings
        )

    assert len(results) == 5
    assert all(result.status == "success" for result in results)


async def test_publish_to_all_handles_partial_failure(settings):

    with (
        patch.object(FacebookPlatform, "publish", new_callable=AsyncMock) as mock_fb,
        patch.object(MastodonPlatform, "publish", new_callable=AsyncMock) as mock_mastodon,
        patch.object(BlueskyPlatform, "publish", new_callable=AsyncMock) as mock_bsky,
        patch.object(DevToPlatform, "publish", new_callable=AsyncMock) as mock_devto,
        patch.object(TelegramPlatform, "publish", new_callable=AsyncMock) as mock_telegram
    ):
        mock_fb.return_value = PublishResult(platform="facebook", status="success")
        mock_mastodon.return_value = PublishResult(platform="mastodon", status="failed", error="Mastodon failed")
        mock_bsky.return_value = PublishResult(platform="bluesky", status="success")
        mock_devto.return_value = PublishResult(platform="devto", status="failed", error="DEV.to failed")
        mock_telegram.return_value = PublishResult(platform="telegram", status="success")

        results = await publish_to_all(
            "Test message https://example.com", "https://example.com", settings
        )

    assert len(results) == 5
    assert sum(r.status == "success" for r in results) == 3
    assert sum(r.status == "failed" for r in results) == 2


async def test_publish_to_all_handles_unexpected_exception(settings):

    with (
        patch.object(FacebookPlatform, "publish", new_callable=AsyncMock) as mock_fb,
        patch.object(MastodonPlatform, "publish", new_callable=AsyncMock) as mock_mastodon,
        patch.object(BlueskyPlatform, "publish", new_callable=AsyncMock) as mock_bsky,
        patch.object(DevToPlatform, "publish", new_callable=AsyncMock) as mock_devto,
        patch.object(TelegramPlatform, "publish", new_callable=AsyncMock) as mock_telegram
    ):
        mock_fb.return_value = PublishResult(platform="facebook", status="success")
        mock_mastodon.side_effect = Exception("Unexpected Mastodon error")
        mock_bsky.return_value = PublishResult(platform="bluesky", status="success")
        mock_devto.return_value = PublishResult(platform="devto", status="success")
        mock_telegram.return_value = PublishResult(platform="telegram", status="success")

        results = await publish_to_all(
            "Test message https://example.com", "https://example.com", settings
        )

    assert len(results) == 5

    mastodon_result = next(r for r in results if r.platform == "mastodon")

    assert mastodon_result.status == "failed"
    assert "Unexpected Mastodon error" in mastodon_result.error
    assert sum(r.status == "success" for r in results) == 4
