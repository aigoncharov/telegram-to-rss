from peewee import SqliteDatabase, Model
from telegram_to_rss.config import db_path

feeds_db = SqliteDatabase(db_path, autoconnect=False)


# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage.
class BaseModel(Model):
    class Meta:
        database = feeds_db
