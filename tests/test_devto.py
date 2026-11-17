import httpx

from unittest.mock import AsyncMock, MagicMock, patch

from app.platforms.devto import DevToPlatform


async def test_devto_publish_success(settings):

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "id": 12345,
        "url": "https://dev.to/testuser/my-new-article",
        "published": True,
        "published_at": "2024-01-15T10:30:00Z"
    }

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ) as mock_post:

        platform = DevToPlatform(settings)
        result = await platform.publish(
            "Check out our new product launch https://example.com",
            "https://example.com"
        )

    assert result.status == "success"
    assert result.platform == "devto"
    assert result.post_id == "12345"
    assert result.posted_url == "https://dev.to/testuser/my-new-article"
    assert result.public_access is True
    assert result.date == "2024-01-15"
    assert result.time == "10:30:00"

    mock_post.assert_awaited_once()


async def test_devto_publish_api_failure(settings):

    mock_response = MagicMock()

    request = httpx.Request("POST", "https://dev.to/api/articles")
    actual_response = httpx.Response(401, request=request)

    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Unauthorized", request=request, response=actual_response
    )

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=mock_response
    ):

        platform = DevToPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None
    assert result.posted_url is None


def test_devto_body_markdown_does_not_duplicate_cta_link(settings):

    platform = DevToPlatform(settings)
    message = "Check out our product https://example.com"
    cta_link = "https://example.com"

    body = platform._create_body_markdown(message, cta_link)

    assert body.count(cta_link) == 1
    assert body == message


def test_devto_extract_title_with_period(settings):

    platform = DevToPlatform(settings)
    message = (
        "Introducing our new product. "
        "Check out all the features at https://example.com"
    )

    title = platform._extract_title(message)

    assert title == "Introducing our new product"


def test_devto_extract_title_truncates_at_60(settings):

    platform = DevToPlatform(settings)
    message = "A" * 100

    title = platform._extract_title(message)

    assert len(title) == 60
    assert title == "A" * 60
