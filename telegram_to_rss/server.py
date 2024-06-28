from quart import Quart
from telegram_to_rss.client import TelegramToRssClient
from telegram_to_rss.config import api_hash, api_id, session_path

app = Quart(__name__)
client = TelegramToRssClient(
    session_path=session_path, api_id=api_id, api_hash=api_hash
)


@app.before_serving
async def startup():
    app.add_background_task(client.start)


@app.after_serving
async def cleanup():
    await client.stop()


@app.route("/")
async def root():
    if client.qr_code_url is not None:
        return {"qr_code_url": client.qr_code_url}

    return await client.list_dialogs()
