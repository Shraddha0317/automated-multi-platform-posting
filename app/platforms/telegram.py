from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform, PublishResult


class TelegramPlatform(BasePlatform):

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "telegram"

    async def publish(self, message: str, cta_link: str) -> PublishResult:

        api_url = (
            f"https://api.telegram.org/"
            f"bot{self.settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        )

        payload = {
            "chat_id": self.settings.TELEGRAM_CHANNEL_ID,
            "text": message
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                response = await client.post(api_url, json=payload)

                response.raise_for_status()

                data = response.json()

                if not data.get("ok"):
                    raise ValueError(
                        data.get("description", "Telegram API request failed")
                    )

                result = data["result"]
                message_id = result["message_id"]
                chat = result["chat"]

                username = chat.get("username")

                if not username:
                    raise ValueError(
                        "Telegram channel must have a public username"
                    )

                username = username.lstrip("@")
                posted_url = f"https://t.me/{username}/{message_id}"

                telegram_date = result.get("date")

                if isinstance(telegram_date, (int, float)):
                    dt = datetime.fromtimestamp(
                        telegram_date, tz=timezone.utc
                    )
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")
                else:
                    date_str = None
                    time_str = None

                return PublishResult(
                    platform=self.name,
                    status="success",
                    post_id=str(message_id),
                    posted_url=posted_url,
                    date=date_str,
                    time=time_str,
                    public_access=True
                )

        except Exception as exc:

            safe_error = str(exc).replace(
                self.settings.TELEGRAM_BOT_TOKEN,
                "[REDACTED]"
            )

            return PublishResult(
                platform=self.name,
                status="failed",
                error=f"{type(exc).__name__}: {safe_error}"
            )
