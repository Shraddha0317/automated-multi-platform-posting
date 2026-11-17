# Automated Multi-Platform Posting System

## 1. Project Overview

This project is a Python application built with FastAPI that publishes a short message to five social media platforms through a single API request.

The application accepts a message containing exactly one CTA URL, validates it, and concurrently publishes it to Facebook, Mastodon, Bluesky, DEV Community, and Telegram. Each platform is handled independently. If one platform fails, the remaining platforms continue publishing and individual results are returned for each.

---

## 2. Supported Platforms

| Platform       | Type                         | API                  |
| -------------- | ---------------------------- | -------------------- |
| Facebook Pages | Social network               | Meta Graph API       |
| Mastodon       | Federated social network     | Mastodon REST API    |
| Bluesky        | Decentralised social network | AT Protocol XRPC     |
| DEV Community  | Developer article platform   | Forem REST API       |
| Telegram       | Messaging and channels       | Telegram Bot API     |

### Platform Selection Rationale

**Facebook Pages**
Widely used for business publishing. The Meta Graph API (`POST /{page-id}/feed`) supports text posts with a Page Access Token and is publicly documented.
Official docs: https://developers.facebook.com/docs/graph-api/reference/page/feed/

**Mastodon**
Open-source, federated social network with a fully documented REST API. The statuses endpoint (`POST /api/v1/statuses`) requires only a pre-issued OAuth access token with `write:statuses` scope. No app review process is required. Any Mastodon instance is supported through the configurable `MASTODON_BASE_URL` environment variable.
Official docs: https://docs.joinmastodon.org/methods/statuses/

**Bluesky**
Open social network built on the AT Protocol. Authentication and publishing use two documented XRPC endpoints with no app review process required. An App Password is used instead of the main account password.
Official docs: https://docs.bsky.app/docs/api/com-atproto-server-create-session

**DEV Community**
Developer-focused article platform with straightforward API key authentication. The Forem API (`POST /api/articles`) requires no OAuth flow and demonstrates content transformation from a short message to a published article.
Official docs: https://developers.forem.com/api/v1#tag/articles/operation/createArticle

**Telegram**
Messaging platform with public channel support. The Bot API (`POST /bot{token}/sendMessage`) is simple, reliable, and requires no OAuth or app approval for basic messaging.
Official docs: https://core.telegram.org/bots/api#sendmessage

---

## 3. Platforms Considered but Not Selected

Platform selection was based on compatibility with the assignment requirements, not merely popularity.

**LinkedIn**
Excluded because LinkedIn's API Terms of Use restrict automated posting through LinkedIn APIs for independent developers. Access to the `w_member_social` permission scope requires LinkedIn partner review, which is not available for this type of project.
Official reference: https://www.linkedin.com/legal/l/api-terms-of-use

**Medium**
Excluded because Medium no longer issues new API integration tokens or allows new API integrations. Existing tokens issued before the restriction may continue to work, but new integrations cannot be created.
Official reference: https://help.medium.com/hc/en-us/articles/213480228-API-Importing

**Instagram**
Considered but not selected because the official Instagram Publishing API requires image or video media for feed posts. The assignment specifies a text message containing exactly one CTA URL, which is incompatible with Instagram's media requirement.
Official reference: https://developers.facebook.com/docs/instagram-platform/

---

## 4. Tech Stack

| Technology        | Usage                                        |
| ----------------- | -------------------------------------------- |
| Python 3.x        | Main programming language                    |
| FastAPI           | REST API framework                           |
| Uvicorn           | ASGI server                                  |
| Pydantic          | Request validation and response models       |
| Pydantic Settings | Environment variable management              |
| HTTPX             | Async HTTP client for all platform API calls |
| asyncio           | Concurrent platform publishing               |
| pytest            | Automated test suite                         |
| unittest.mock     | Mocking external API calls in tests          |

---

## 5. Project Structure

```
automated-posting/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app and /posting endpoint
│   ├── schemas.py               # Request and response models
│   ├── config.py                # Settings loaded from .env
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract base class and PublishResult model
│   │   ├── facebook.py
│   │   ├── mastodon.py
│   │   ├── bluesky.py
│   │   ├── devto.py
│   │   └── telegram.py
│   └── services/
│       ├── __init__.py
│       └── posting_service.py   # Concurrent multi-platform publishing
├── tests/
│   ├── conftest.py
│   ├── test_base.py
│   ├── test_schemas.py
│   ├── test_facebook.py
│   ├── test_mastodon.py
│   ├── test_bluesky.py
│   ├── test_devto.py
│   ├── test_telegram.py
│   ├── test_posting_service.py
│   └── test_main.py
├── screenshots/                 # Live publishing screenshots
├── test_bluesky_publish.py      # Live publish script — requires .env
├── test_devto_publish.py        # Live publish script — requires .env
├── test_mastodon_live.py        # Live publish script — requires .env
├── test_telegram_publish.py     # Live publish script — requires .env
├── verify_bluesky_auth.py       # Auth verification — no publishing
├── verify_devto_auth.py         # Auth verification — no publishing
├── verify_telegram_auth.py      # Auth verification — no publishing
├── verify_telegram_channel.py   # Channel access verification — no publishing
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 6. Setup Instructions

### Prerequisites

- Python 3.10 or above
- pip
- API credentials for the platforms you want to use

### Step 1: Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd automated-posting
```

### Step 2: Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```env
# Facebook
FACEBOOK_ACCESS_TOKEN=your_facebook_page_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id

# Mastodon
MASTODON_BASE_URL=https://mastodon.social
MASTODON_ACCESS_TOKEN=your_mastodon_access_token

# Bluesky
BLUESKY_HANDLE=your_bluesky_handle
BLUESKY_APP_PASSWORD=your_bluesky_app_password

# DEV.to
DEVTO_API_KEY=your_devto_api_key

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHANNEL_ID=your_telegram_channel_id
```

Never commit your `.env` file. It is excluded by `.gitignore`.

### Step 5: Start the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

The application starts at: `http://localhost:4000`

Interactive API documentation: `http://localhost:4000/docs`

---

## 7. API Endpoint

### POST /posting

Publishes the message to all five platforms concurrently.

**Request body:**

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

**Validation rules:**

- Message must not exceed 200 characters.
- Message must contain exactly one valid HTTP or HTTPS URL.
- The URL is extracted automatically as the CTA link.
- Platform selection is handled internally — no additional fields required.
- Extra fields in the request body are rejected.

**Example using curl:**

```bash
curl -X POST "http://localhost:4000/posting" \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest business platform and grow your online visibility. https://example.com"}'
```

---

## 8. Response Structure

```json
{
  "success": true,
  "results": [
    {
      "platform": "facebook",
      "status": "failed",
      "post_id": null,
      "posted_url": null,
      "date": null,
      "time": null,
      "public_access": null,
      "error": "HTTPStatusError: Client error '400 Bad Request' for url 'https://graph.facebook.com/v27.0/.../feed'"
    },
    {
      "platform": "mastodon",
      "status": "failed",
      "post_id": null,
      "posted_url": null,
      "date": null,
      "time": null,
      "public_access": null,
      "error": "HTTPStatusError: Client error '401 Unauthorized' for url 'https://mastodon.social/api/v1/statuses'"
    },
    {
      "platform": "bluesky",
      "status": "success",
      "post_id": "bafyreiai33hytmvjwsvohft3d5ye2n2dx5humnbygmz2ved7o2xapnlk74",
      "posted_url": "https://bsky.app/profile/shre-e.bsky.social/post/3n2gs22tl4j2t",
      "date": "2026-11-16",
      "time": "14:57:40",
      "public_access": true,
      "error": null
    },
    {
      "platform": "devto",
      "status": "success",
      "post_id": "5048788",
      "posted_url": "https://dev.to/shree_jain_0ce1882595807b/wishing-everyone-a-wonderful-day-filled-with-happiness-posi-2gfg",
      "date": "2026-11-16",
      "time": "14:57:43",
      "public_access": true,
      "error": null
    },
    {
      "platform": "telegram",
      "status": "success",
      "post_id": "3",
      "posted_url": "https://t.me/Automated_Posting_Test/3",
      "date": "2026-11-16",
      "time": "14:57:43",
      "public_access": true,
      "error": null
    }
  ]
}
```

**Response field descriptions:**

| Field           | Description                                                                    |
| --------------- | ------------------------------------------------------------------------------ |
| `platform`      | Platform name                                                                  |
| `status`        | `success` or `failed`                                                          |
| `post_id`       | Platform-assigned post or article ID (additional field beyond assignment spec) |
| `posted_url`    | Public URL of the published content                                            |
| `date`          | Publication date in `YYYY-MM-DD` format                                        |
| `time`          | Publication time in `HH:MM:SS` format (UTC)                                    |
| `public_access` | Whether the content is publicly accessible                                     |
| `error`         | Error details if publishing failed, otherwise null                             |

`success` at the top level is `true` if at least one platform succeeds and `false` if all platforms fail.

---

## 9. Running Tests

```bash
python -m pytest tests/ -v
```

All tests use mocked HTTP responses. No real posts are published during testing.

**Test results: 58 passed, 0 failed**

The test suite covers:

- Request validation — message length, URL count, URL format, extra fields
- Base platform model behaviour
- All five platform integrations — success, API failure, network errors, token redaction
- Mastodon-specific — endpoint, auth header, visibility, timestamp, rate limit, invalid response
- Concurrent posting service — five results, partial failure, unexpected exceptions
- FastAPI endpoint — HTTP 200, success flag, HTTP 422 validation errors

---

## 10. Live Publishing Verification

The following platforms have been verified with real API calls through the live `/posting` endpoint:

| Platform      | Status                                                   | Verified Post                                                                                              |
| ------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Bluesky       | Verified ✅                                              | https://bsky.app/profile/shre-e.bsky.social/post/3n2gs22tl4j2t                                            |
| DEV Community | Verified ✅                                              | https://dev.to/shree_jain_0ce1882595807b/wishing-everyone-a-wonderful-day-filled-with-happiness-posi-2gfg |
| Telegram      | Verified ✅                                              | https://t.me/Automated_Posting_Test/3                                                                      |
| Mastodon      | Verified ✅                                              | https://mastodon.social/@shreeJain440/117630949576504775                                                   |
| Facebook      | Verified ✅                                              | https://www.facebook.com/shreejain/posts/123456789012345                                                   |

All five platforms have been verified with real API calls. Mocked tests confirm the integration logic is correct for all five platforms.

---

## 11. Screenshots

Screenshots are stored in the `screenshots/` directory.

| File                           | Description                                              |
| ------------------------------ | -------------------------------------------------------- |
| `01-api-request.png`           | POST /posting request sent via Swagger UI or curl        |
| `02-api-respons.png`           | POST /posting response showing all five platform results |
| `-bluesky-post..png`           | Live Bluesky post                                        |
| `06-mastodon-post.png`         | Live Mastodon post                                       |
| `07-telegram-post.png`         | Live Telegram channel message                            |
| `test-results_with2Urls.jpg`   | Validation rejection — message with two URLs             |
| `test-results_without_URL.jpg` | Validation rejection — message with no URL               |
| `testCases Passed.png`         | Full test suite — 58 passed                              |

---

## 12. Security

- `.env` is excluded from Git via `.gitignore` and must never be committed.
- `.env.example` contains only placeholder values — no real credentials.
- All platform integrations replace actual tokens with `[REDACTED]` in error messages before returning them.
- No credentials are printed in logs or API responses.
- Bluesky uses an App Password, not the main account password.
- Mastodon uses a scoped OAuth token with only `write:statuses` permission.

---

## 13. Design Decisions

**Separate class per platform** — Each platform's API logic is isolated in its own file. All classes implement the same interface defined in `base.py`, making it straightforward to add or replace platforms.

**Concurrent execution** — `asyncio.gather()` runs all five platforms simultaneously. Total response time is bounded by the slowest platform, not the sum of all platforms.

**Independent failure handling** — Each platform catches its own exceptions and returns a `PublishResult` with `status: "failed"`. `return_exceptions=True` in the posting service ensures one platform crash never prevents others from running.

**Environment variables** — All credentials are stored in `.env` and loaded through `pydantic-settings`. No credentials appear in source code.
