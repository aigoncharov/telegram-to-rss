import asyncio
from quart import Quart, render_template
from telegram_to_rss.client import TelegramToRssClient
from telegram_to_rss.config import api_hash, api_id, session_path, password
from telegram_to_rss.qr_code import get_qr_code_image

app = Quart(__name__)
client = TelegramToRssClient(
    session_path=session_path, api_id=api_id, api_hash=api_hash, password=password
)


@app.before_serving
async def startup():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start())


@app.after_serving
async def cleanup():
    await client.stop()


@app.route("/")
async def root():
    if client.qr_code_url is not None:
        qr_code_image = get_qr_code_image(client.qr_code_url)
        return await render_template("qr_code.html", qr_code=qr_code_image)

    feeds = await client.list_dialogs()
    return await render_template("feeds.html", user=client.user, feeds=feeds)
