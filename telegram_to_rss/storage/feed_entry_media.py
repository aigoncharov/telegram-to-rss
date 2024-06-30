from .base import BaseModel
from .feed_entry import FeedEntry
from peewee import IntegerField, TextField, ForeignKeyField


class FeedEntryMedia(BaseModel):
    id = IntegerField(primary_key=True)
    feed_entry = ForeignKeyField(FeedEntry, on_delete="cascade", backref="media")
    path = TextField()
