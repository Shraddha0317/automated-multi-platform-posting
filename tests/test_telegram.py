import httpx

from unittest.mock import AsyncMock, MagicMock, patch

from app.platforms.telegram import TelegramPlatform


async def test_telegram_publish_success(settings):

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 123,
            "chat": {
                "id": -1001234567890,
                "username": "yourchannel"
            },
            "text": "Visit https://example.com",
            "date": 1730000000
        }
    }

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ) as mock_post:

        platform = TelegramPlatform(settings)
        result = await platform.publish(
            "Visit https://example.com",
            "https://example.com"
        )

    assert result.status == "success"
    assert result.platform == "telegram"
    assert result.post_id == "123"
    assert result.posted_url == "https://t.me/yourchannel/123"
    assert result.public_access is True
    assert result.error is None
    assert result.date is not None
    assert result.time is not None

    mock_post.assert_awaited_once()


async def test_telegram_publish_api_failure(settings):

    mock_response = MagicMock()

    request = httpx.Request(
        "POST",
        "https://api.telegram.org/bottest-token/sendMessage"
    )

    actual_response = httpx.Response(403, request=request)

    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Forbidden", request=request, response=actual_response
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ):

        platform = TelegramPlatform(settings)
        result = await platform.publish(
            "Visit https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None
    assert result.posted_url is None


async def test_telegram_publish_missing_username(settings):

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "ok": True,
        "result": {
            "message_id": 456,
            "chat": {"id": -1001234567890},
            "text": "Visit https://example.com"
        }
    }

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ):

        platform = TelegramPlatform(settings)
        result = await platform.publish(
            "Visit https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None
    assert "public username" in result.error
    assert result.public_access is None
