# WARNING: Running this script publishes a real message to Telegram. Requires .env with valid credentials.

import asyncio

from app.config import get_settings
from app.platforms.telegram import TelegramPlatform

MESSAGE = "Hello! This is a test message. https://example.com"
CTA_LINK = "https://example.com"


async def main():
    settings = get_settings()
    platform = TelegramPlatform(settings)

    print("Publishing to Telegram...")
    print("Channel :", settings.TELEGRAM_CHANNEL_ID)
    print("Message :", MESSAGE)
    print()

    result = await platform.publish(MESSAGE, CTA_LINK)

    if result.status == "success":
        print("Message published successfully!")
        print("Message ID :", result.post_id)
        print("URL        :", result.posted_url)
        print("Date       :", result.date)
        print("Time       :", result.time)
    else:
        print("Publishing failed.")
        print("Error      :", result.error)


if __name__ == "__main__":
    asyncio.run(main())
