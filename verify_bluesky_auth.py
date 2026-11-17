import asyncio
import httpx

from app.config import get_settings

ENDPOINT = "https://bsky.social/xrpc/com.atproto.server.createSession"


async def main():
    settings = get_settings()

    handle = settings.BLUESKY_HANDLE
    password = settings.BLUESKY_APP_PASSWORD

    # Safe diagnostics — never prints the actual password
    print("--- Diagnostics ---")
    print("Handle loaded    :", bool(handle))
    print("Handle value     :", handle)
    print("Password loaded  :", bool(password))
    print("Password length  :", len(password))
    print("Whitespace check :", "CLEAN" if password == password.strip() else "WARNING: surrounding whitespace detected")
    print("Endpoint         :", ENDPOINT)
    print("-------------------")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                ENDPOINT,
                json={"identifier": handle, "password": password},
            )

            if response.status_code == 200:
                data = response.json()
                print("\nAuthentication successful!")
                print("Handle :", data.get("handle"))
                print("DID    :", data.get("did"))
                print("Token received:", bool(data.get("accessJwt")))

            elif response.status_code == 401:
                print("\nAuthentication failed (401).")
                print("Bluesky says: Invalid identifier or password.")
                print("Action: generate a new app password at https://bsky.app -> Settings -> App Passwords")

            else:
                print("\nUnexpected response.")
                print("HTTP status:", response.status_code)
                # Strip any token-like values from the error body before printing
                error_body = response.text
                print("Error:", error_body)

    except httpx.RequestError as exc:
        print("Network error:", type(exc).__name__, str(exc))


if __name__ == "__main__":
    asyncio.run(main())
