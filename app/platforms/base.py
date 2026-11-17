
from abc import ABC, abstractmethod

from pydantic import BaseModel


class PublishResult(BaseModel):
    platform: str
    status: str
    post_id: str | None = None
    posted_url: str | None = None
    date: str | None = None
    time: str | None = None
    public_access: bool | None = None
    error: str | None = None


class BasePlatform(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the platform name."""
        pass

    @abstractmethod
    async def publish(
        self,
        message: str,
        cta_link: str
    ) -> PublishResult:
        """Publish a message to the platform."""
        pass
