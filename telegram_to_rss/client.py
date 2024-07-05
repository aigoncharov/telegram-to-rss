from telethon import TelegramClient, types, errors, custom
from telegram_to_rss.consts import TELEGRAM_NOTIFICATIONS_DIALOG_ID
from telethon.utils import resolve_id
from telegram_to_rss.consts import MESSAGE_FETCH_HARD_LIMIT
import logging


class TelegramToRssClient:
    _telethon: TelegramClient
    _qr_code_url: str | None = None
    _user: types.User = None
    _password: str | None = None

    def __init__(
        self, session_path: str, api_id: int, api_hash: str, password: str | None = None
    ):
        self._telethon = TelegramClient(
            session=session_path, api_id=api_id, api_hash=api_hash
        )
        self._telethon.parse_mode = "html"
        self._password = password

    async def start(self):
        await self._telethon.connect()
        is_authorized = await self._telethon.is_user_authorized()

        if not is_authorized:
            try:
                qr_login_req = await self._telethon.qr_login()
                self._qr_code_url = qr_login_req.url
                await qr_login_req.wait()
            except errors.SessionPasswordNeededError:
                if self._password is None:
                    raise Exception(
                        "2FA enabled and requires a password, but no password is provided."
                    )
                await self._telethon.sign_in(password=self._password)

        self._qr_code_url = None
        self._user = await self._telethon.get_me()

    async def stop(self):
        if self._telethon.is_connected():
            await self._telethon.disconnect()

    async def list_dialogs(self) -> list[custom.Dialog]:
        all_dialogs = await self._telethon.get_dialogs()
        filtered_dialogs = [
            dialog
            for dialog in all_dialogs
            if (
                dialog.id != TELEGRAM_NOTIFICATIONS_DIALOG_ID
                and dialog.entity.id != self._user.id
            )
        ]
        return filtered_dialogs

    async def get_dialog_messages(
        self,
        dialog: custom.Dialog,
        limit: int = MESSAGE_FETCH_HARD_LIMIT,
        min_message_id: int = 0,
    ) -> list[custom.Message]:
        limit = min(MESSAGE_FETCH_HARD_LIMIT, limit)

        logging.debug(
            "TelegramToRssClient.get_dialog_messages %s (%s) %s %s",
            dialog.name,
            dialog.id,
            limit,
            min_message_id,
        )

        messages: list[custom.Message] = await self._telethon.iter_messages(
            dialog, limit=limit, min_id=min_message_id
        ).collect()
        return messages

    @property
    def qr_code_url(self):
        return self._qr_code_url

    @property
    def user(self):
        return self._user


def telethon_dialog_id_to_tg_id(id: int):
    return resolve_id(id)[0]
