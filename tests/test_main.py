from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.config import get_settings
from app.platforms.base import PublishResult


client = TestClient(app)


def test_post_endpoint_returns_200(settings):

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        mock_results = [
            PublishResult(platform="facebook", status="success"),
            PublishResult(platform="mastodon", status="success"),
            PublishResult(platform="bluesky", status="success"),
            PublishResult(platform="devto", status="success"),
            PublishResult(platform="telegram", status="success")
        ]

        with patch(
            "app.main.publish_to_all",
            new_callable=AsyncMock
        ) as mock_publish:

            mock_publish.return_value = mock_results

            response = client.post(
                "/posting",
                json={"message": "Explore our latest update https://example.com"}
            )

        assert response.status_code == 200

        response_data = response.json()

        assert "success" in response_data
        assert response_data["success"] is True
        assert "results" in response_data
        assert len(response_data["results"]) == 5
        assert all(
            r["status"] == "success"
            for r in response_data["results"]
        )

        mock_publish.assert_awaited_once()

    finally:
        app.dependency_overrides = previous_overrides


def test_post_endpoint_returns_success_false_when_all_fail(settings):

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        mock_results = [
            PublishResult(platform="facebook", status="failed", error="err"),
            PublishResult(platform="mastodon", status="failed", error="err"),
            PublishResult(platform="bluesky", status="failed", error="err"),
            PublishResult(platform="devto", status="failed", error="err"),
            PublishResult(platform="telegram", status="failed", error="err")
        ]

        with patch(
            "app.main.publish_to_all",
            new_callable=AsyncMock
        ) as mock_publish:

            mock_publish.return_value = mock_results

            response = client.post(
                "/posting",
                json={"message": "Explore our latest update https://example.com"}
            )

        assert response.status_code == 200
        assert response.json()["success"] is False

    finally:
        app.dependency_overrides = previous_overrides


def test_post_endpoint_validates_message_length(settings):

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        response = client.post(
            "/posting",
            json={"message": "A" * 201}
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides = previous_overrides


def test_post_endpoint_rejects_message_without_link(settings):

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        response = client.post(
            "/posting",
            json={"message": "This message has no link"}
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides = previous_overrides


def test_post_endpoint_rejects_message_with_multiple_links(settings):

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_settings] = lambda: settings

    try:
        response = client.post(
            "/posting",
            json={"message": "Visit https://one.com and https://two.com"}
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides = previous_overrides
