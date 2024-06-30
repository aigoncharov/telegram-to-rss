from tortoise.models import Model
from tortoise import fields
from tortoise.signals import post_delete
from typing import Type
from anyio import Path


class FeedEntryMedia(Model):
    id = fields.TextField(primary_key=True)
    feed_entry = fields.ForeignKeyField(
        "models.FeedEntry", on_delete=fields.CASCADE, related_name="media"
    )
    path = fields.TextField()


@post_delete
async def remove_associated_file(
    sender: Type[FeedEntryMedia],
    instance: FeedEntryMedia,
) -> None:
    await Path(instance.path).unlink()
