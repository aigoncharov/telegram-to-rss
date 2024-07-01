from tortoise.models import Model
from tortoise import fields
from .feed_entry import FeedEntry


class Feed(Model):
    id = fields.IntField(primary_key=True)
    name = fields.TextField()
    last_update = fields.DatetimeField(auto_now=True)
    entries: fields.ReverseRelation[FeedEntry]
