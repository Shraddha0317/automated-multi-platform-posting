from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform, PublishResult


class FacebookPlatform(BasePlatform):

    API_VERSION = "v27.0"

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "facebook"

    async def publish(
        self,
        message: str,
        cta_link: str
    ) -> PublishResult:

        api_url = (
            f"https://graph.facebook.com/"
            f"{self.API_VERSION}/"
            f"{self.settings.FACEBOOK_PAGE_ID}/feed"
        )

        payload = {
            "message": message,
            "access_token": self.settings.FACEBOOK_ACCESS_TOKEN
        }

        params = {"fields": "id,created_time"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                response = await client.post(
                    api_url,
                    json=payload,
                    params=params
                )

                response.raise_for_status()

                data = response.json()

                post_id = data["id"]
                posted_url = f"https://www.facebook.com/{post_id}"

                created_time_raw = data.get("created_time")

                if created_time_raw:
                    dt = datetime.fromisoformat(
                        created_time_raw.replace("Z", "+00:00")
                    )
                else:
                    dt = datetime.now(timezone.utc)

                return PublishResult(
                    platform=self.name,
                    status="success",
                    post_id=post_id,
                    posted_url=posted_url,
                    date=dt.strftime("%Y-%m-%d"),
                    time=dt.strftime("%H:%M:%S"),
                    public_access=True
                )

        except Exception as exc:

            token = self.settings.FACEBOOK_ACCESS_TOKEN

            safe_error = (
                str(exc).replace(token, "[REDACTED]")
                if len(token) > 8
                else str(exc)
            )

            return PublishResult(
                platform=self.name,
                status="failed",
                error=f"{type(exc).__name__}: {safe_error}"
            )
