from tortoise import fields
from tortoise.models import Model

class Operation(Model):
    id = fields.IntField(pk=True)
    ticker = fields.CharField(max_length=10)
    buy_date = fields.DatetimeField()
    sell_date = fields.DatetimeField()
    capital_invested = fields.FloatField()
    capital_gained = fields.FloatField()
    wallet = fields.ForeignKeyField('models.Wallet', related_name='operations', on_delete=fields.CASCADE)

    class Meta:
        table = "operations"
