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

    async def bulk_delete_feeds(self, ids: list[int]):
        if len(ids) != 0:
            await Feed.filter(Q(id__in=list(ids))).delete()

    @atomic()
    async def create_feed(self, dialog: custom.Dialog):
        feed = await Feed.create(id=dialog.id, name=dialog.name)

        dialog_messages = await self._client.get_dialog_messages(
            dialog=dialog, message_limit=self._message_limit
        )
        feed_entries = await self._process_new_dialog_messages(feed, dialog_messages)

        await FeedEntry.bulk_create(feed_entries)

    @atomic()
    async def update_feed(self, dialog: custom.Dialog):
        feed = await Feed.get(id=dialog.id)
        last_feed_entry = await FeedEntry.filter(feed=feed).order_by("-date").first()

        [_, tg_message_id] = parse_feed_entry_id(last_feed_entry.id)
        new_dialog_messages = await self._client.get_dialog_messages(
            dialog=dialog,
            message_limit=self._message_limit,
            min_message_id=tg_message_id,
        )

        feed_entries = await self._process_new_dialog_messages(
            feed, new_dialog_messages
        )

        await FeedEntry.bulk_create(feed_entries)
        # Save even if unchanged to update date
        await feed.save()

        old_feed_entries = (
            await FeedEntry.all().offset(self._message_limit).order_by("-date")
        )
        await FeedEntry.filter(
            Q(id__in=[entry.id for entry in old_feed_entries])
        ).delete()

    async def _process_new_dialog_messages(
        self, feed: Feed, dialog_messages: list[custom.Message]
    ):
        filtered_dialog_messages: list[custom.Message] = []
        for dialog_message in dialog_messages:
            dialog_message.downloaded_media = []

            if (
                dialog_message.grouped_id is None
                or len(filtered_dialog_messages) == 0
                or dialog_message.grouped_id != filtered_dialog_messages[-1].grouped_id
            ):
                filtered_dialog_messages.append(dialog_message)

            if (
                len(filtered_dialog_messages) != 0
                and dialog_message.grouped_id == filtered_dialog_messages[-1].grouped_id
                and len(dialog_message.text) > len(filtered_dialog_messages[-1].text)
            ):
                filtered_dialog_messages[-1].text = dialog_message.text

            last_processed_message = filtered_dialog_messages[-1]
            if dialog_message.photo:
                feed_entry_media_id = "{}-{}".format(
                    to_feed_entry_id(feed, dialog_message),
                    len(last_processed_message.downloaded_media),
                )
                media_path = self._static_path.joinpath(feed_entry_media_id)
                res_path = await dialog_message.download_media(file=media_path)
                last_processed_message.downloaded_media.append(Path(res_path).name)

        feed_entries: list[FeedEntry] = []
        for dialog_message in filtered_dialog_messages:
            feed_entry_id = to_feed_entry_id(feed, dialog_message)
            feed_entries.append(
                FeedEntry(
                    id=feed_entry_id,
                    feed=feed,
                    message=dialog_message.text,
                    date=dialog_message.date,
                    media=dialog_message.downloaded_media,
                )
            )

        return feed_entries


def to_feed_entry_id(feed: Feed, dialog_message: custom.Message):
    return "{}--{}".format(feed.id, dialog_message.id)


def parse_feed_entry_id(id: str):
    [channel_id, message_id] = id.split("--")
    return (int(channel_id), int(message_id))


async def update_feeds_in_db(telegram_poller: TelegramPoller):
    [feed_ids_to_delete, feeds_to_create, feeds_to_update] = (
        await telegram_poller.fetch_dialogs()
    )

    await telegram_poller.bulk_delete_feeds(feed_ids_to_delete)

    for feed_to_create in feeds_to_create:
        await telegram_poller.create_feed(feed_to_create)

    for feed_to_update in feeds_to_update:
        await telegram_poller.update_feed(feed_to_update)
