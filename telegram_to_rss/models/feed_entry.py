import logging
from tortoise.models import Model
from tortoise import fields
from tortoise.signals import post_delete
from typing import Type
from anyio import Path
from telegram_to_rss.config import static_path


class FeedEntry(Model):
    id = fields.TextField(primary_key=True)
    feed = fields.ForeignKeyField(
        "models.Feed", on_delete=fields.CASCADE, related_name="entries"
    )
    message = fields.TextField()
    date = fields.DatetimeField()
    media = fields.JSONField(default=[])
    has_unsupported_media = fields.BooleanField(default=False)


@post_delete(FeedEntry)
async def remove_associated_file(
    sender: Type[FeedEntry],
    instance: FeedEntry,
    using_db
) -> None:
    try:
        for media_relative_path in instance.media:
            file_path = Path(static_path).joinpath(media_relative_path)
            await file_path.unlink(missing_ok=True)
            logging.debug(f"File removed: {file_path}")

    except Exception as e:
        logging.error(f"Error while removing FeedEntry id {instance.id}: {e}")
