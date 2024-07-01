import asyncio
from quart import Quart, render_template
from telegram_to_rss.client import TelegramToRssClient
from telegram_to_rss.config import (
    api_hash,
    api_id,
    session_path,
    password,
    static_path,
    message_limit,
    update_interval_seconds,
)
from telegram_to_rss.qr_code import get_qr_code_image
from telegram_to_rss.db import init_feeds_db, close_feeds_db
from telegram_to_rss.generate_feed import update_feeds_cache
from telegram_to_rss.poll_telegram import TelegramPoller, update_feeds_in_db
from telegram_to_rss.models import Feed

app = Quart(__name__, static_folder=static_path, static_url_path="/static")
client = TelegramToRssClient(
    session_path=session_path, api_id=api_id, api_hash=api_hash, password=password
)
telegram_poller = TelegramPoller(
    client=client, message_limit=message_limit, static_path=static_path
)
update_rss_task: asyncio.Task | None = None


async def start_rss_generation():
    global update_rss_task

    async def update_rss():
        global update_rss_task

        await update_feeds_in_db(telegram_poller=telegram_poller)
        await update_feeds_cache(feed_render_dir=static_path)

        await asyncio.sleep(update_interval_seconds)

        loop = asyncio.get_event_loop()
        update_rss_task = loop.create_task(update_rss())

    await client.start()

    loop = asyncio.get_event_loop()
    update_rss_task = loop.create_task(update_rss())
    await update_rss_task


@app.before_serving
async def startup():
    await init_feeds_db()
    is_authorized = await client.connect()
    if is_authorized:
        await start_rss_generation()
    else:
        loop = asyncio.get_event_loop()
        loop.create_task(start_rss_generation())


@app.after_serving
async def cleanup():
    if update_rss_task is not None:
        update_rss_task.cancel()
    await client.disconnect()
    await close_feeds_db()


@app.route("/")
async def root():
    if client.qr_code_url is not None:
        qr_code_image = get_qr_code_image(client.qr_code_url)
        return await render_template("qr_code.html", qr_code=qr_code_image)

    feeds = await Feed.all()
    return await render_template("feeds.html", user=client.user, feeds=feeds)
