import pytest
from pydantic import ValidationError

from app.schemas import PostRequest


def test_valid_request():
    request = PostRequest(
        message="Check out my website https://example.com"
    )
    assert request.message == "Check out my website https://example.com"
    assert request.extract_cta_link() == "https://example.com"


def test_extract_cta_link_returns_url_from_message():
    request = PostRequest(message="Visit https://example.com today")
    assert request.extract_cta_link() == "https://example.com"


def test_message_over_200_characters():
    with pytest.raises(ValidationError):
        PostRequest(message="A" * 201)


def test_message_with_no_link_is_rejected():
    with pytest.raises(ValidationError):
        PostRequest(message="Check out my website")


def test_message_with_multiple_links_is_rejected():
    with pytest.raises(ValidationError):
        PostRequest(
            message="Visit https://example.com and also https://other.com"
        )


def test_message_with_exactly_one_link_passes():
    request = PostRequest(message="Visit https://example.com")
    assert request.extract_cta_link() == "https://example.com"


def test_url_with_trailing_period_is_cleaned():
    request = PostRequest(
        message="Check out https://example.com."
    )
    assert request.extract_cta_link() == "https://example.com"


def test_url_with_trailing_comma_is_cleaned():
    request = PostRequest(
        message="Visit https://example.com, it is great"
    )
    assert request.extract_cta_link() == "https://example.com"


def test_url_with_trailing_parenthesis_is_cleaned():
    request = PostRequest(
        message="See this (https://example.com)"
    )
    assert request.extract_cta_link() == "https://example.com"


def test_malformed_url_without_scheme_is_rejected():
    with pytest.raises(ValidationError):
        PostRequest(message="Visit example.com for more info")


def test_ftp_url_is_rejected():
    with pytest.raises(ValidationError):
        PostRequest(message="Download from ftp://example.com today")


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        PostRequest(
            message="Visit https://example.com",
            cta_link="https://example.com"
        )
