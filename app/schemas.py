import re

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, TypeAdapter, model_validator
from pydantic import ValidationError as PydanticValidationError
from app.platforms.base import PublishResult

_URL_PATTERN = re.compile(r'https?://[^\s]+')
_URL_VALIDATOR = TypeAdapter(AnyHttpUrl)
_TRAILING_PUNCT = re.compile(r'[.,;:!?)\'\"]+$')


def _extract_urls(text: str) -> list[str]:
    candidates = _URL_PATTERN.findall(text)
    cleaned = [_TRAILING_PUNCT.sub("", u) for u in candidates]
    valid = []
    for url in cleaned:
        try:
            _URL_VALIDATOR.validate_python(url)
            valid.append(url)
        except PydanticValidationError:
            pass
    return valid


class PostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., max_length=200)

    @model_validator(mode="after")
    def validate_exactly_one_cta_link(self):
        urls = _extract_urls(self.message)
        if len(urls) == 0:
            raise ValueError("Message must contain exactly one CTA link")
        if len(urls) > 1:
            raise ValueError("Message must contain exactly one CTA link")
        return self

    def extract_cta_link(self) -> str:
        return _extract_urls(self.message)[0]


class PostResponse(BaseModel):
    success: bool
    results: list[PublishResult]
