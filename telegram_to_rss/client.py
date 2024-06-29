from telethon import TelegramClient, types, errors

from telegram_to_rss.consts import TELEGRAM_NOTIFICATIONS_DIALOG_ID


class TelegramToRssClient:
    __telethon: TelegramClient
    __qr_code_url: str | None = None
    __user: types.User | None = None
    __password: str | None = None

    def __init__(
        self, session_path: str, api_id: int, api_hash: str, password: str | None = None
    ):
        self.__telethon = TelegramClient(
            session=session_path, api_id=api_id, api_hash=api_hash
        )
        self.__password = password

    async def start(self):
        await self.__telethon.connect()
        is_authorized = await self.__telethon.is_user_authorized()

        if not is_authorized:
            try:
                qr_login_req = await self.__telethon.qr_login()
                self.__qr_code_url = qr_login_req.url
                await qr_login_req.wait()
            except errors.SessionPasswordNeededError:
                if self.__password is None:
                    raise Exception(
                        "2FA enabled and requires a password, but no password is provided."
                    )
                await self.__telethon.sign_in(password=self.__password)

        self.__qr_code_url = None
        self.__user = await self.__telethon.get_me()

    async def stop(self):
        if self.__telethon.is_connected():
            await self.__telethon.disconnect()

    async def list_dialogs(self):
        all_dialogs = await self.__telethon.get_dialogs()
        filtered_dialogs = [
            dialog
            for dialog in all_dialogs
            if (
                dialog.id != TELEGRAM_NOTIFICATIONS_DIALOG_ID
                and dialog.entity.id != self.__user.id
            )
        ]
        return filtered_dialogs

    @property
    def qr_code_url(self):
        return self.__qr_code_url

    @property
    def user(self):
        return self.__user
