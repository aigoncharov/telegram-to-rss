from .base import BaseModel
from .feed import Feed
from peewee import DateTimeField, IntegerField, TextField, ForeignKeyField


class FeedEntry(BaseModel):
    id = TextField(primary_key=True)
    feed = ForeignKeyField(Feed, on_delete="cascade", backref="entries")
    message = TextField()
    date = DateTimeField()
    grouped_id = IntegerField(null=True)
