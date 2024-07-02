from feedgen.feed import FeedGenerator
from pathlib import Path
from quart import utils
from telegram_to_rss.models import Feed, FeedEntry
from tortoise.query_utils import Prefetch
from shutil import copy
from telegram_to_rss.config import base_url
from telegram_to_rss.poll_telegram import parse_feed_entry_id
import re

CLEAN_TITLE = re.compile("<.*?>")


def clean_title(raw_html):
    cleantext = re.sub(CLEAN_TITLE, "", raw_html).replace("\n", " ").strip()
    return cleantext


def generate_feed(feed_render_dir: Path, feed: Feed):
    feed_id = "{}/static/{}.xml".format(base_url, feed.id)

    fg = FeedGenerator()
    fg.id(feed_id)
    fg.title(feed.name)
    fg.updated(feed.last_update)
    fg.link(href=feed_id, rel="self")
    fg.description(feed.name)

    for feed_entry in feed.entries:
        feed_entry_id = "https://t.me/c/{}/{}".format(
            *parse_feed_entry_id(feed_entry.id)
        )

        fe = fg.add_entry()
        fe.id(feed_entry_id)

        message_text = clean_title(feed_entry.message)
        title = message_text[:100]
        fe.title(title)

        images = ""
        for media_path in feed_entry.media:
            media_url = "{}/static/{}".format(base_url, media_path)
            images += '<br /><img src="{}"/>'.format(media_url)

        fe.content(feed_entry.message.replace("\n", "<br />") + images)
        fe.updated(feed_entry.date)
        fe.link(href=feed_entry_id, rel="alternate")

    tmp_feed_file = feed_render_dir.joinpath("{}-tmp.xml".format(feed.id))
    fg.atom_file(tmp_feed_file)

    final_feed_file = feed_render_dir.joinpath("{}.xml".format(feed.id))
    copy(tmp_feed_file, final_feed_file)
    Path.unlink(tmp_feed_file)


async def update_feeds_cache(feed_render_dir: str):
    feeds = await Feed.all().prefetch_related(
        Prefetch("entries", queryset=FeedEntry.all().order_by("date"))
    )

    for feed in feeds:
        await utils.run_sync(generate_feed)(feed_render_dir, feed)
