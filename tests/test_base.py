import pytest
from app.platforms.base import BasePlatform, PublishResult


def test_successful_publish_result():
    result = PublishResult(
        platform="facebook",
        status="success",
        post_id="12345",
        posted_url="https://facebook.com/post/12345"
    )

    assert result.platform == "facebook"
    assert result.status == "success"
    assert result.post_id == "12345"
    assert result.posted_url == "https://facebook.com/post/12345"


def test_failed_publish_result():
    result = PublishResult(
        platform="mastodon",
        status="failed",
        error="Authentication failed"
    )

    assert result.platform == "mastodon"
    assert result.status == "failed"
    assert result.error == "Authentication failed"


def test_optional_fields_default_to_none():
    result = PublishResult(
        platform="bluesky",
        status="failed"
    )

    assert result.post_id is None
    assert result.posted_url is None
    assert result.date is None
    assert result.time is None
    assert result.public_access is None
    assert result.error is None


def test_valid_platform_subclass_can_be_instantiated():

    class FacebookPlatform(BasePlatform):

        @property
        def name(self) -> str:
            return "facebook"

        async def publish(self, message: str, cta_link: str) -> PublishResult:
            return PublishResult(
                platform=self.name,
                status="success",
                post_id="12345"
            )

    platform = FacebookPlatform()

    assert platform.name == "facebook"
    assert isinstance(platform, BasePlatform)


def test_incomplete_platform_subclass_cannot_be_instantiated():

    class IncompletePlatform(BasePlatform):

        @property
        def name(self) -> str:
            return "Incomplete"

    with pytest.raises(TypeError):
        IncompletePlatform()


async def test_publish_returns_correct_result():

    class FacebookPlatform(BasePlatform):

        @property
        def name(self) -> str:
            return "facebook"

        async def publish(self, message: str, cta_link: str) -> PublishResult:
            return PublishResult(
                platform=self.name,
                status="success",
                post_id="12345"
            )

    platform = FacebookPlatform()
    result = await platform.publish("Hello https://example.com", "https://example.com")

    assert result.status == "success"
    assert result.platform == "facebook"
    assert result.post_id == "12345"
