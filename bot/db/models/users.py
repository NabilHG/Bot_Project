from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(pk=True)    
    name = fields.CharField(max_length=50) # from Telegram
    username = fields.CharField(max_length=50) # choosen nick
    phone = fields.CharField(max_length=9) 
    register_date = fields.DatetimeField(auto_now_add=True)
    expeling_date = fields.DatetimeField(null=True)
    investor_profile = fields.FloatField(null=True)
    is_admin = fields.BooleanField()

    class Meta:
        table = "users"
