from telethon import TelegramClient, types


class TelegramToRssClient:
    __telethon: TelegramClient
    __qr_code_url: str | None = None
    __user: types.User | None = None

    def __init__(self, session_path: str, api_id: int, api_hash: str):
        self.__telethon = TelegramClient(session_path, api_id, api_hash)

    async def start(self):
        await self.__telethon.connect()
        is_authorized = await self.__telethon.is_user_authorized()

        if not is_authorized:
            qr_login_req = await self.__telethon.qr_login()
            self.__qr_code_url = qr_login_req.url
            await qr_login_req.wait()

        self.__qr_code_url = None
        self.__user = await self.__telethon.get_me()

    async def stop(self):
        if self.__telethon.is_connected():
            await self.__telethon.disconnect()

    async def list_dialogs(self):
        dialogs = {}
        async for dialog in self.__telethon.iter_dialogs():
            dialogs[dialog.id] = dialog
        return dialogs

    @property
    def qr_code_url(self):
        return self.__qr_code_url

    @property
    def user(self):
        return self.__user
