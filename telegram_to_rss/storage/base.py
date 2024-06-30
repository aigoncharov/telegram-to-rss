from peewee import SqliteDatabase, Model
from telegram_to_rss.config import db_path

feeds_db = SqliteDatabase(db_path, autoconnect=False)


class BaseModel(Model):
    class Meta:
        database = feeds_db
