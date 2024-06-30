from peewee import SqliteDatabase
from telegram_to_rss.storage import Feed
from feedgen.feed import FeedGenerator
from pathlib import Path


class FeedGenerator:
    _feeds_db: SqliteDatabase
    _feed_render_dir: Path

    def __init__(self, feeds_db: SqliteDatabase, feed_render_dir: Path) -> None:
        self._feeds_db = feeds_db
        self._feed_render_dir = feed_render_dir

    def run(self):
        for feed in Feed.select():
            self._process_feed(feed)

    def _process_feed(self, feed):
        fg = FeedGenerator()
        fg.id("tgrss://{}".format(feed.id))
        fg.title(feed.name)
        fg.lastBuildDate(feed.last_update)

        for feed_entry in feed.entries:
            fe = fg.add_entry()
            fe.id("tgrss://{}".format(feed_entry.id))
            fe.content(feed_entry.message)
            fe.published(feed_entry.date)

        feed_file = self._feed_render_dir.joinpath("rss_{}.xml".format(feed.id))
        fg.rss_file(feed_file)
