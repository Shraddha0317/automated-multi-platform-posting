import httpx
import pytest

from unittest.mock import AsyncMock, MagicMock, patch

from app.platforms.mastodon import MastodonPlatform


MASTODON_URL = "https://mastodon.social/api/v1/statuses"
MESSAGE = "Check out our product https://example.com"
CTA_LINK = "https://example.com"


def make_success_response(
    status_id="123456789",
    url="https://mastodon.social/@testuser/123456789",
    visibility="public",
    created_at="2026-11-16T11:00:00.000Z"
):
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {
        "id": status_id,
        "url": url,
        "visibility": visibility,
        "created_at": created_at,
        "content": MESSAGE
    }
    return mock


def make_http_error(status_code: int):
    request = httpx.Request("POST", MASTODON_URL)
    response = httpx.Response(status_code, request=request)
    mock = MagicMock()
    mock.raise_for_status.side_effect = httpx.HTTPStatusError(
        f"HTTP {status_code}", request=request, response=response
    )
    return mock


async def test_mastodon_publish_success(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response()) as mock_post:

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "success"
    assert result.platform == "mastodon"
    mock_post.assert_awaited_once()


async def test_mastodon_correct_endpoint_and_payload(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response()) as mock_post:

        await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    call_kwargs = mock_post.call_args
    assert call_kwargs.args[0] == "https://mastodon.social/api/v1/statuses"
    payload = call_kwargs.kwargs["json"]
    assert payload["status"] == MESSAGE
    assert payload["visibility"] == "public"


async def test_mastodon_correct_auth_header(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response()) as mock_post:

        await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    headers = mock_post.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer test-mastodon-token"


async def test_mastodon_public_visibility_in_payload(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response()) as mock_post:

        await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    payload = mock_post.call_args.kwargs["json"]
    assert payload["visibility"] == "public"


async def test_mastodon_response_parsing(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response()):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "success"
    assert result.error is None
    assert result.public_access is True


async def test_mastodon_status_id_extraction(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response(status_id="987654321")):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.post_id == "987654321"


async def test_mastodon_url_extraction(settings):
    expected_url = "https://mastodon.social/@testuser/987654321"
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response(url=expected_url)):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.posted_url == expected_url


async def test_mastodon_timestamp_extraction(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response(created_at="2026-11-16T11:00:00.000Z")):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.date == "2026-11-16"
    assert result.time == "11:00:00"


async def test_mastodon_auth_failure(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_http_error(401)):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "failed"
    assert result.error is not None
    assert result.posted_url is None


async def test_mastodon_rate_limit(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_http_error(429)):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "failed"
    assert result.error is not None


async def test_mastodon_network_timeout(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               side_effect=httpx.TimeoutException("timed out")):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "failed"
    assert "TimeoutException" in result.error


async def test_mastodon_network_failure(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               side_effect=httpx.ConnectError("connection refused")):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "failed"
    assert result.error is not None


async def test_mastodon_invalid_response(settings):
    mock = MagicMock()
    mock.raise_for_status.return_value = None
    mock.json.return_value = {}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.status == "failed"
    assert result.error is not None


async def test_mastodon_cta_url_preserved(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response()) as mock_post:

        await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    payload = mock_post.call_args.kwargs["json"]
    assert payload["status"].count(CTA_LINK) == 1
    assert payload["status"] == MESSAGE


async def test_mastodon_public_access_true_when_public(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response(visibility="public")):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.public_access is True


async def test_mastodon_public_access_false_when_unlisted(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_success_response(visibility="unlisted")):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert result.public_access is False


async def test_mastodon_token_not_in_error(settings):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock,
               return_value=make_http_error(401)):

        result = await MastodonPlatform(settings).publish(MESSAGE, CTA_LINK)

    assert "test-mastodon-token" not in (result.error or "")
