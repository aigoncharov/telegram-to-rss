from telegram_to_rss.client import TelegramToRssClient, custom
from telegram_to_rss.models import Feed, FeedEntry
from tortoise.expressions import Q


class TelegramPoller:
    _client: TelegramToRssClient

    def __init__(self, client: TelegramToRssClient) -> None:
        self._client = client

    async def fetch_dialogs(self):
        tg_dialogs = await self._client.list_dialogs()
        db_feeds = await Feed.all()

        tg_dialogs_ids = set([dialog.id for dialog in tg_dialogs])
        db_feeds_ids = set([feed.id for feed in db_feeds])

        feed_ids_to_delete = db_feeds_ids - tg_dialogs_ids
        feed_ids_to_create = tg_dialogs_ids - db_feeds_ids
        feed_ids_to_update = db_feeds_ids.intersection(tg_dialogs_ids)

        feeds_to_create = [
            dialog for dialog in tg_dialogs if dialog.id in feed_ids_to_create
        ]
        feeds_to_update = [
            dialog for dialog in tg_dialogs if dialog.id in feed_ids_to_update
        ]

        return (list(feed_ids_to_delete), feeds_to_create, feeds_to_update)

    async def bulk_delete_feeds(ids: list[int]):
        if len(ids) != 0:
            await Feed.filter(Q(id__in=list(ids))).delete()

    async def create_feed(self, dialog: custom.Dialog):
        feed = await Feed.create(id=dialog.id, name=dialog.name)

        dialog_messages = await self._client.get_dialog_messages(dialog=dialog)

        dialog_messages_grouped_ids = {}
        for dialog_message in dialog_messages:
            if dialog_messages_grouped_ids[dialog_message.grouped_id] is None:
                dialog_messages_grouped_ids[dialog_message.grouped_id] = {
                    "strategy": "merge",
                    "message": None,
                    "media": [],
                    "id": dialog_message.id,
                }

            if (
                dialog_messages_grouped_ids[dialog_message.grouped_id].strategy
                == "split"
            ):
                continue

            if dialog_message.message is not None:
                if (
                    dialog_messages_grouped_ids[dialog_message.grouped_id].message
                    is not None
                ):
                    dialog_messages_grouped_ids[dialog_message.grouped_id].strategy = (
                        "split"
                    )
                    continue
                else:
                    dialog_messages_grouped_ids[dialog_message.grouped_id].message = (
                        dialog_message.message
                    )

            if dialog_message.photo:
                media = await dialog_message.download_media()
                dialog_messages_grouped_ids[dialog_message.grouped_id].media.append(
                    media
                )

        feed_entries = [
            FeedEntry(
                id="{}/{}".format(feed.id, dialog_message.id),
                feed=feed,
                message=dialog_message.message,
                date=dialog_message.date,
                grouped_id=dialog_message.grouped_id,
            )
            for dialog_message in dialog_messages
        ]
        await FeedEntry.bulk_create(feed_entries)
