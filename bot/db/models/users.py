from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True) # from Telegram id
    nombre = fields.CharField(max_length=50) # from Telegram
    username = fields.CharField(max_length=50, null=True) # choosen nick
    phone = fields.CharField(max_lenght=9) #From Telegram id
    register_date = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"
