from .base import BaseModel
from .feed import Feed
from peewee import DateTimeField, IntegerField, TextField, ForeignKeyField


class FeedEntry(BaseModel):
    id = IntegerField(primary_key=True)
    feed = ForeignKeyField(Feed, on_delete="cascade", backref="items")
    message = TextField()
    date = DateTimeField()
