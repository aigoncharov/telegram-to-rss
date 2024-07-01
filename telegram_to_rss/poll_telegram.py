from telegram_to_rss.client import TelegramToRssClient, custom
from telegram_to_rss.models import Feed, FeedEntry
from tortoise.expressions import Q
from tortoise.transactions import atomic
from pathlib import Path


class TelegramPoller:
    _client: TelegramToRssClient
    _message_limit: int
    _static_path: Path

    def __init__(
        self, client: TelegramToRssClient, message_limit: int, static_path: Path
    ) -> None:
        self._client = client
        self._message_limit = message_limit
        self._static_path = static_path

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

    @atomic
    async def create_feed(self, dialog: custom.Dialog):
        feed = await Feed.create(id=dialog.id, name=dialog.name)

        dialog_messages = await self._client.get_dialog_messages(
            dialog=dialog, message_limit=self._message_limit
        )
        [feed_entries, feed_entries_media] = await self._process_new_dialog_messages(
            feed, dialog_messages
        )

        await FeedEntry.bulk_create(feed_entries)
        await FeedEntry.bulk_create(feed_entries_media)

    @atomic
    async def update_feed(self, dialog: custom.Dialog):
        feed = await Feed.get(id=dialog.id)
        [last_message] = await FeedEntry.filter(feed=feed).order_by("-date").limit(1)

        new_dialog_messages = await self._client.get_dialog_messages(
            dialog=dialog,
            message_limit=self._message_limit,
            min_message_id=last_message.id,
        )

        [feed_entries, feed_entries_media] = await self._process_new_dialog_messages(
            feed, new_dialog_messages
        )

        await FeedEntry.bulk_create(feed_entries)
        await FeedEntry.bulk_create(feed_entries_media)

        await FeedEntry.all().order_by("-date").offset(self._message_limit).delete()

    async def _process_new_dialog_messages(
        self, feed: Feed, dialog_messages: list[custom.Message]
    ):
        filtered_dialog_messages = []
        for dialog_message in dialog_messages:
            last_processed_message = filtered_dialog_messages[-1]
            if (
                dialog_message.grouped_id is None
                or last_processed_message is None
                or dialog_message.grouped_id != last_processed_message.grouped_id
            ):
                filtered_dialog_messages.append(dialog_message)

            last_processed_message = filtered_dialog_messages[-1]
            if dialog_message.photo:
                if last_processed_message.get("downloaded_media", None) is None:
                    last_processed_message.downloaded_media = []

                feed_entry_media_id = "{}-{}-{}".format(
                    feed.id,
                    dialog_message.id,
                    len(last_processed_message.downloaded_media),
                )
                media_path = self._static_path.joinpath(feed_entry_media_id)
                await dialog_message.download_media(file=media_path)
                last_processed_message.downloaded_media.append(feed_entry_media_id)

        feed_entries: list[FeedEntry] = []
        for dialog_message in filtered_dialog_messages:
            feed_entry_id = "{}-{}".format(feed.id, dialog_message.id)
            feed_entries.append(
                FeedEntry(
                    id=feed_entry_id,
                    feed=feed,
                    message=dialog_message.message,
                    date=dialog_message.date,
                    media=dialog_message.get("downloaded_media", []),
                )
            )

        return feed_entries


async def update_feeds_in_db(telegram_poller: TelegramPoller):
    [feed_ids_to_delete, feeds_to_create, feeds_to_update] = (
        await telegram_poller.fetch_dialogs()
    )

    await telegram_poller.bulk_delete_feeds(feed_ids_to_delete)

    for feed_to_create in feeds_to_create:
        await telegram_poller.create_feed(feed_to_create)

    for feed_to_update in feeds_to_update:
        await telegram_poller.update_feed(feed_to_update)
