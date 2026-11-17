
import asyncio

from app.config import Settings
from app.platforms.base import PublishResult
from app.platforms.facebook import FacebookPlatform
from app.platforms.mastodon import MastodonPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.telegram import TelegramPlatform


async def publish_to_all(
    message: str,
    cta_link: str,
    settings: Settings
) -> list[PublishResult]:

    # 1. Instantiate all five platforms
    platforms = [
        FacebookPlatform(settings),
        MastodonPlatform(settings),
        BlueskyPlatform(settings),
        DevToPlatform(settings),
        TelegramPlatform(settings)
    ]

    # 2. Create a coroutine for each platform
    tasks = [
        platform.publish(message, cta_link)
        for platform in platforms
    ]

    # 3. Execute all publishing operations concurrently
    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    # 4. Handle unexpected exceptions defensively
    final_results = []

    for platform, result in zip(platforms, results):

        if isinstance(result, Exception):
            final_results.append(
                PublishResult(
                    platform=platform.name,
                    status="failed",
                    error=f"{type(result).__name__}: {str(result)}"
                )
            )
        else:
            final_results.append(result)

    # 5. Return one result per platform
    return final_results
