from .feed import Feed
from .feed_entry import FeedEntry
from .feed_entry_media import FeedEntryMedia
from .base import *


def init_feeds_db():
    feeds_db.connect()
    feeds_db.create_tables([Feed, FeedEntry, FeedEntryMedia])
    return feeds_db
