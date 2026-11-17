from datetime import datetime

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform, PublishResult


class DevToPlatform(BasePlatform):

    API_URL = "https://dev.to/api/articles"

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "devto"

    def _extract_title(self, message: str) -> str:
        title = message.split(".")[0].strip()
        return title[:60].strip()

    def _create_body_markdown(
        self,
        message: str,
        cta_link: str
    ) -> str:
        return message

    async def publish(
        self,
        message: str,
        cta_link: str
    ) -> PublishResult:

        title = self._extract_title(message)
        body_markdown = self._create_body_markdown(message, cta_link)

        payload = {
            "article": {
                "title": title,
                "body_markdown": body_markdown,
                "published": True
            }
        }

        headers = {
            "api-key": self.settings.DEVTO_API_KEY,
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                response = await client.post(
                    self.API_URL,
                    json=payload,
                    headers=headers
                )

                response.raise_for_status()

                data = response.json()

                article_id = data["id"]
                posted_url = data["url"]

                published_at_raw = data.get("published_at")

                if published_at_raw:
                    dt = datetime.fromisoformat(
                        published_at_raw.replace("Z", "+00:00")
                    )
                    date_str = dt.strftime("%Y-%m-%d")
                    time_str = dt.strftime("%H:%M:%S")
                else:
                    date_str = None
                    time_str = None

                return PublishResult(
                    platform=self.name,
                    status="success",
                    post_id=str(article_id),
                    posted_url=posted_url,
                    date=date_str,
                    time=time_str,
                    public_access=True
                )

        except Exception as exc:

            safe_error = str(exc).replace(
                self.settings.DEVTO_API_KEY,
                "[REDACTED]"
            )

            return PublishResult(
                platform=self.name,
                status="failed",
                error=f"{type(exc).__name__}: {safe_error}"
            )
