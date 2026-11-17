import httpx

from unittest.mock import AsyncMock, MagicMock, patch

from app.platforms.bluesky import BlueskyPlatform


def create_mock_response(response_data):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = response_data
    return mock_response


def create_http_error(status_code=401):
    request = httpx.Request("POST", "https://bsky.social/xrpc/test")
    response = httpx.Response(status_code, request=request)
    return httpx.HTTPStatusError(
        "API request failed", request=request, response=response
    )


async def test_bluesky_publish_success(settings):

    auth_response = create_mock_response({
        "accessJwt": "test-access-jwt",
        "did": "did:plc:abc123"
    })

    post_response = create_mock_response({
        "uri": "at://did:plc:abc123/app.bsky.feed.post/xyz789",
        "cid": "bafytest123"
    })

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock
    ) as mock_client_post:

        mock_client_post.side_effect = [auth_response, post_response]

        platform = BlueskyPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "success"
    assert result.platform == "bluesky"
    assert result.post_id == "bafytest123"
    assert result.posted_url == (
        f"https://bsky.app/profile/{settings.BLUESKY_HANDLE}/post/xyz789"
    )
    assert result.public_access is True
    assert mock_client_post.await_count == 2


async def test_bluesky_auth_failure(settings):

    auth_response = MagicMock()
    auth_response.raise_for_status.side_effect = create_http_error()

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock,
        return_value=auth_response
    ):

        platform = BlueskyPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None


async def test_bluesky_post_failure(settings):

    auth_response = create_mock_response({
        "accessJwt": "test-access-jwt",
        "did": "did:plc:abc123"
    })

    post_response = MagicMock()
    post_response.raise_for_status.side_effect = create_http_error(403)

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock
    ) as mock_client_post:

        mock_client_post.side_effect = [auth_response, post_response]

        platform = BlueskyPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    assert result.status == "failed"
    assert result.error is not None
    assert mock_client_post.await_count == 2


async def test_bluesky_published_url_format(settings):

    auth_response = create_mock_response({
        "accessJwt": "test-access-jwt",
        "did": "did:plc:abc123"
    })

    post_response = create_mock_response({
        "uri": "at://did:plc:abc123/app.bsky.feed.post/xyz789",
        "cid": "bafytest123"
    })

    with patch(
        "httpx.AsyncClient.post",
        new_callable=AsyncMock
    ) as mock_client_post:

        mock_client_post.side_effect = [auth_response, post_response]

        platform = BlueskyPlatform(settings)
        result = await platform.publish(
            "Check out our product https://example.com",
            "https://example.com"
        )

    expected_url = (
        f"https://bsky.app/profile/"
        f"{settings.BLUESKY_HANDLE}/post/xyz789"
    )

    assert result.status == "success"
    assert result.posted_url == expected_url
