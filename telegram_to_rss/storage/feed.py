from .base import BaseModel
from peewee import DateTimeField, IntegerField, TextField


class Feed(BaseModel):
    id = IntegerField(primary_key=True)
    name = TextField()
    last_update = DateTimeField()
