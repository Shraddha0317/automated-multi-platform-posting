# WARNING: Running this script publishes a real article to DEV.to. Requires .env with valid credentials.

import asyncio

from app.config import get_settings
from app.platforms.devto import DevToPlatform

MESSAGE = "Hello! This is a test message. https://example.com"
CTA_LINK = "https://example.com"


async def main():
    settings = get_settings()
    platform = DevToPlatform(settings)

    print("Publishing to DEV.to...")
    print("Message :", MESSAGE)
    print()

    result = await platform.publish(MESSAGE, CTA_LINK)

    if result.status == "success":
        print("Article published successfully!")
        print("Article ID :", result.post_id)
        print("URL        :", result.posted_url)
        print("Date       :", result.date)
        print("Time       :", result.time)
    else:
        print("Publishing failed.")
        print("Error      :", result.error)


if __name__ == "__main__":
    asyncio.run(main())
