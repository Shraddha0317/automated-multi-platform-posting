import asyncio
import httpx

from app.config import get_settings


async def main():
    settings = get_settings()

    token = settings.TELEGRAM_BOT_TOKEN
    channel = settings.TELEGRAM_CHANNEL_ID

    base_url = f"https://api.telegram.org/bot{token}"

    async with httpx.AsyncClient(timeout=20.0) as client:

        # Step 1: Retrieve the bot's own ID dynamically
        me_response = await client.get(f"{base_url}/getMe")
        me_data = me_response.json()

        if not me_data.get("ok"):
            print("Failed to retrieve bot identity:")
            print(me_data.get("description", "Unknown error"))
            return

        bot_id = me_data["result"]["id"]

        # Step 2: Verify the channel exists and is accessible
        chat_response = await client.get(
            f"{base_url}/getChat",
            params={"chat_id": channel}
        )

        chat_data = chat_response.json()

        if not chat_data.get("ok"):
            print("Channel access failed:")
            print(chat_data.get("description", "Unknown error"))
            return

        chat = chat_data["result"]

        print("Channel found   :", chat.get("title"))
        print("Channel username:", chat.get("username"))

        # Step 3: Verify bot administrator permissions using the dynamic ID
        member_response = await client.get(
            f"{base_url}/getChatMember",
            params={"chat_id": channel, "user_id": bot_id}
        )

        member_data = member_response.json()

        if not member_data.get("ok"):
            print("Administrator verification failed:")
            print(member_data.get("description", "Unknown error"))
            return

        member = member_data["result"]

        print("Bot status      :", member.get("status"))
        print("Can post messages:", member.get("can_post_messages"))


if __name__ == "__main__":
    asyncio.run(main())
