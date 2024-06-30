from telegram_to_rss.models import Feed
from feedgen.feed import FeedGenerator
from pathlib import Path


def generate_feed(feed_render_dir: Path):
    for feed in Feed.select():
        fg = FeedGenerator()
        fg.id("tgrss://{}".format(feed.id))
        fg.title(feed.name)
        fg.lastBuildDate(feed.last_update)

        for feed_entry in feed.entries:
            fe = fg.add_entry()
            fe.id("tgrss://{}".format(feed_entry.id))
            fe.content(feed_entry.message)
            fe.published(feed_entry.date)

        feed_file = feed_render_dir.joinpath("rss_{}.xml".format(feed.id))
        fg.rss_file(feed_file)
