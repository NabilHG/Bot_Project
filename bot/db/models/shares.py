from tortoise import fields
from tortoise.models import Model

class Share(Model):
    id = fields.IntField(pk=True)
    ticker = fields.CharField(max_length=10)

    class Meta:
        table = "shares"