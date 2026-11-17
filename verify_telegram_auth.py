
import asyncio
import httpx

from app.config import get_settings


async def main():
    settings = get_settings()

    token = settings.TELEGRAM_BOT_TOKEN

    if not token:
        print("Telegram bot token is missing.")
        return

    url = f"https://api.telegram.org/bot{token}/getMe"

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url)
            data = response.json()

            if response.status_code == 200 and data.get("ok"):
                bot = data["result"]

                print("Telegram authentication successful!")
                print("Bot username:", bot.get("username"))
                print("Bot ID:", bot.get("id"))
                print("Is bot:", bot.get("is_bot"))
            else:
                print("Authentication failed.")
                print("HTTP status:", response.status_code)
                print("Error:", data.get("description", "Unknown error"))

    except httpx.RequestError as exc:
        print("Network error:", type(exc).__name__)


if __name__ == "__main__":
    asyncio.run(main())
