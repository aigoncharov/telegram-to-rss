from feedgen.feed import FeedGenerator
from pathlib import Path
from quart import utils
from telegram_to_rss.models import Feed


def generate_feed(feed_render_dir: Path, feed):
    fg = FeedGenerator()
    fg.id("tgrss://{}".format(feed.id))
    fg.title(feed.name)
    fg.lastBuildDate(feed.last_update)

    for feed_entry in feed.entries:
        fe = fg.add_entry()
        fe.id("tgrss://{}".format(feed_entry.id))
        fe.content(feed_entry.message)
        fe.published(feed_entry.date)

    feed_file = feed_render_dir.joinpath("{}.rss.xml".format(feed.id))
    fg.rss_file(feed_file)


async def update_feeds_cache(feed_render_dir: str):
    feeds = await Feed.all()
    for feed in feeds:
        await feed.fetch_related("entries")
        await utils.run_sync(generate_feed)(feed_render_dir, feed)
