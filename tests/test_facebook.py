import httpx

from unittest.mock import AsyncMock, MagicMock, patch

from app.platforms.facebook import FacebookPlatform


async def test_facebook_publish_success(settings):

    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "123456789_987654321",
        "created_time": "2024-01-15T10:30:00+0000"
    }

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ) as mock_post:

        platform = FacebookPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "success"
    assert result.platform == "facebook"
    assert result.post_id == "123456789_987654321"
    assert result.posted_url == "https://www.facebook.com/123456789_987654321"
    assert result.public_access is True
    assert result.date is not None
    assert result.time is not None
    assert result.error is None

    mock_post.assert_awaited_once()


async def test_facebook_publish_api_failure(settings):

    mock_response = MagicMock()

    request = httpx.Request(
        "POST",
        "https://graph.facebook.com/v27.0/123456789/feed"
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

        platform = FacebookPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None


async def test_facebook_token_redacted_in_error(settings):

    token = settings.FACEBOOK_ACCESS_TOKEN

    mock_response = MagicMock()

    request = httpx.Request(
        "POST",
        "https://graph.facebook.com/v27.0/123456789/feed"
    )
    actual_response = httpx.Response(403, request=request)

    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"Request failed with token {token}",
        request=request,
        response=actual_response
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ):

        platform = FacebookPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None
    assert token not in result.error
    assert "[REDACTED]" in result.error
