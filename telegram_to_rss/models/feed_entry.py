from tortoise.models import Model
from tortoise import fields


class FeedEntry(Model):
    id = fields.TextField(primary_key=True)
    feed = fields.ForeignKeyField(
        "models.Feed", on_delete=fields.CASCADE, related_name="entries"
    )
    message = fields.TextField()
    date = fields.DatetimeField()
    grouped_id = fields.IntField(null=True)
