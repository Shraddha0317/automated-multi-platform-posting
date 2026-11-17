# WARNING: Running this script publishes a real post to Bluesky. Requires .env with valid credentials.

import asyncio

from app.config import get_settings
from app.platforms.bluesky import BlueskyPlatform

MESSAGE = "Hello! This is a test message. https://example.com"
CTA_LINK = "https://example.com"


async def main():
    settings = get_settings()
    platform = BlueskyPlatform(settings)

    print("Publishing to Bluesky...")
    print("Message :", MESSAGE)
    print("Account :", settings.BLUESKY_HANDLE)
    print()

    result = await platform.publish(MESSAGE, CTA_LINK)

    if result.status == "success":
        print("Post published successfully!")
        print("Post ID  :", result.post_id)
        print("URL      :", result.posted_url)
        print("Date     :", result.date)
        print("Time     :", result.time)
    else:
        print("Publishing failed.")
        print("Error    :", result.error)


if __name__ == "__main__":
    asyncio.run(main())
