# WARNING: Running this script publishes a real post to Mastodon. Requires .env with valid credentials.

import asyncio

from app.config import get_settings
from app.platforms.mastodon import MastodonPlatform

MESSAGE = (
    "Wishing everyone a wonderful day filled with happiness, "
    "positivity, and new opportunities! https://example.com"
)
CTA_LINK = "https://example.com"


async def main():
    settings = get_settings()
    platform = MastodonPlatform(settings)

    print("Publishing to Mastodon...")
    print("Instance :", settings.MASTODON_BASE_URL)
    print("Message  :", MESSAGE)
    print()

    result = await platform.publish(MESSAGE, CTA_LINK)

    if result.status == "success":
        print("Published successfully!")
        print("Post ID  :", result.post_id)
        print("URL      :", result.posted_url)
        print("Date     :", result.date)
        print("Time     :", result.time)
        print("Public   :", result.public_access)
    else:
        print("Publishing failed.")
        print("Error    :", result.error)


if __name__ == "__main__":
    asyncio.run(main())
