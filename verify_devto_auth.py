
import asyncio
import httpx

from app.config import get_settings


async def main():
    settings = get_settings()

    api_key = settings.DEVTO_API_KEY

    if not api_key:
        print("DEV.to API key is missing.")
        return

    url = "https://dev.to/api/users/me"

    headers = {
        "api-key": api_key,
        "Accept": "application/vnd.forem.api-v1+json",
        "User-Agent": "automated-posting-python"
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                print("DEV.to authentication successful!")
                print("Username:", data.get("username"))
                print("User ID:", data.get("id"))
            else:
                print("Authentication failed.")
                print("HTTP status:", response.status_code)
                print("Error:", response.text)

    except httpx.RequestError as exc:
        print("Network error:", type(exc).__name__)


if __name__ == "__main__":
    asyncio.run(main())
