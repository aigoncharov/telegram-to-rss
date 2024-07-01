from feedgen.feed import FeedGenerator
from pathlib import Path
from quart import utils
from telegram_to_rss.models import Feed, FeedEntry
from tortoise.query_utils import Prefetch
from shutil import copy


def generate_feed(feed_render_dir: Path, feed: Feed):
    fg = FeedGenerator()
    fg.id("tgrss://{}".format(feed.id))
    fg.title(feed.name)
    fg.lastBuildDate(feed.last_update)
    fg.link(href="https://t.me/{}".format(feed.id))
    fg.description(feed.name)

    for feed_entry in feed.entries:
        fe = fg.add_entry()
        fe.id("tgrss://{}".format(feed_entry.id))
        fe.content(feed_entry.message)
        fe.published(feed_entry.date)

    tmp_feed_file = feed_render_dir.joinpath("{}-tmp.rss.xml".format(feed.id))
    fg.rss_file(tmp_feed_file)

    final_feed_file = feed_render_dir.joinpath("{}.rss.xml".format(feed.id))
    copy(tmp_feed_file, final_feed_file)
    Path.unlink(tmp_feed_file)


async def update_feeds_cache(feed_render_dir: str):
    feeds = await Feed.all().prefetch_related(
        Prefetch("entries", queryset=FeedEntry.all().order_by("date"))
    )

    for feed in feeds:
        await utils.run_sync(generate_feed)(feed_render_dir, feed)
