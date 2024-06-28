from telethon import TelegramClient


async def run(client: TelegramClient):
    async for dialog in client.iter_dialogs():
        print(dialog.name, "has ID", dialog.id)


def connect(client: TelegramClient):
    with client:
        client.loop.run_until_complete(run(client))
