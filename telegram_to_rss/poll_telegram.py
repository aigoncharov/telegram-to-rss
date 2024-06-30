from telegram_to_rss.client import TelegramToRssClient


async def poll_telegram(client: TelegramToRssClient):
    dialogs = await client.list_dialogs()
