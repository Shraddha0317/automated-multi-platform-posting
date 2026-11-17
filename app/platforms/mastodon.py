from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform, PublishResult


class MastodonPlatform(BasePlatform):

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "mastodon"

    async def publish(
        self,
        message: str,
        cta_link: str
    ) -> PublishResult:

        url = f"{self.settings.MASTODON_BASE_URL}/api/v1/statuses"

        headers = {
            "Authorization": f"Bearer {self.settings.MASTODON_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "status": message,
            "visibility": "public"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()

                data = response.json()

                post_id = str(data["id"])
                posted_url = data["url"]
                visibility = data.get("visibility", "public")

                created_at_raw = data.get("created_at")

                if created_at_raw:
                    dt = datetime.fromisoformat(
                        created_at_raw.replace("Z", "+00:00")
                    )
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")
                else:
                    dt = datetime.now(timezone.utc)
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")

                return PublishResult(
                    platform=self.name,
                    status="success",
                    post_id=post_id,
                    posted_url=posted_url,
                    date=date_str,
                    time=time_str,
                    public_access=(visibility == "public")
                )

        except Exception as exc:

            token = self.settings.MASTODON_ACCESS_TOKEN
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
