from tortoise.models import Model
from tortoise import fields


class FeedEntryMedia(Model):
    id = fields.IntField(primary_key=True)
    feed_entry = fields.ForeignKeyField(
        "models.FeedEntry", on_delete=fields.CASCADE, related_name="media"
    )
    path = fields.TextField()
