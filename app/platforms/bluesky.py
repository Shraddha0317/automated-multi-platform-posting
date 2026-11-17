from datetime import datetime, timezone

import httpx

from app.config import Settings
from app.platforms.base import BasePlatform, PublishResult


class BlueskyPlatform(BasePlatform):

    BASE_URL = "https://bsky.social/xrpc"

    def __init__(self, settings: Settings):
        self.settings = settings

    @property
    def name(self) -> str:
        return "bluesky"

    async def _authenticate(
        self,
        client: httpx.AsyncClient
    ) -> tuple[str, str]:

        response = await client.post(
            f"{self.BASE_URL}/com.atproto.server.createSession",
            json={
                "identifier": self.settings.BLUESKY_HANDLE,
                "password": self.settings.BLUESKY_APP_PASSWORD
            }
        )

        response.raise_for_status()

        data = response.json()

        return data["accessJwt"], data["did"]

    async def publish(
        self,
        message: str,
        cta_link: str
    ) -> PublishResult:

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:

                access_jwt, did = await self._authenticate(client)

                response = await client.post(
                    f"{self.BASE_URL}/com.atproto.repo.createRecord",
                    headers={"Authorization": f"Bearer {access_jwt}"},
                    json={
                        "repo": did,
                        "collection": "app.bsky.feed.post",
                        "record": {
                            "text": message,
                            "$type": "app.bsky.feed.post",
                            "createdAt": datetime.now(
                                timezone.utc
                            ).isoformat()
                        }
                    }
                )

                response.raise_for_status()

                data = response.json()

                uri = data["uri"]
                cid = data["cid"]
                rkey = uri.split("/")[-1]

                posted_url = (
                    f"https://bsky.app/profile/"
                    f"{self.settings.BLUESKY_HANDLE}/post/{rkey}"
                )

                dt = datetime.now(timezone.utc)

                return PublishResult(
                    platform=self.name,
                    status="success",
                    post_id=cid,
                    posted_url=posted_url,
                    date=dt.strftime("%Y-%m-%d"),
                    time=dt.strftime("%H:%M:%S"),
                    public_access=True
                )

        except Exception as exc:

            safe_error = str(exc).replace(
                self.settings.BLUESKY_APP_PASSWORD,
                "[REDACTED]"
            )

            return PublishResult(
                platform=self.name,
                status="failed",
                error=f"{type(exc).__name__}: {safe_error}"
            )
