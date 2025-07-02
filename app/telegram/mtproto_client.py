from telethon import TelegramClient, events
import os
import asyncio
from loguru import logger

API_ID = int(os.getenv("TELEGRAM_API_ID", "123456"))  # замените на свой
API_HASH = os.getenv("TELEGRAM_API_HASH", "your_api_hash")
SESSION_NAME = os.getenv("TELEGRAM_SESSION", "mtproto_session")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def fetch_new_messages(channel_username, limit=10):
    await client.start()
    messages = []
    async for msg in client.iter_messages(channel_username, limit=limit):
        messages.append({
            "id": msg.id,
            "text": msg.text,
            "date": msg.date,
            "sender_id": msg.sender_id
        })
    await client.disconnect()
    return messages

if __name__ == "__main__":
    # Пример запуска
    import sys
    channel = sys.argv[1] if len(sys.argv) > 1 else "@durov"
    msgs = asyncio.run(fetch_new_messages(channel))
    for m in msgs:
        print(m) 