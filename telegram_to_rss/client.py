from telethon import TelegramClient
import os

# Remember to use your own values from my.telegram.org!
api_id = int(os.environ.get("TG_API_ID"))
api_hash = os.environ.get("TG_API_HASH")
phone = os.environ.get("TG_PHONE")
password = os.environ.get("TG_PASSWORD")


def init_client():
    client = TelegramClient("telegram_to_rss.session", api_id, api_hash).start(
        phone=phone, password=password
    )
    return client
