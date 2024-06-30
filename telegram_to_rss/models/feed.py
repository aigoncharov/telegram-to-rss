from tortoise.models import Model
from tortoise import fields


class Feed(Model):
    id = fields.IntField(primary_key=True)
    name = fields.TextField()
    last_update = fields.DatetimeField()
