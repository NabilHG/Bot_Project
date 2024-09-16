from tortoise import fields
from tortoise.models import Model

class Operation(Model):
    id = fields.BigIntField(pk=True)
    ticker = fields.CharField(max_length=10)
    buy_date = fields.DatetimeField()
    sell_date = fields.DatetimeField(null=True)
    capital_invested = fields.FloatField()
    capital_retrived = fields.FloatField(null=True)
    purchased_price = fields.FloatField(null=True)
    status = fields.CharField(max_length=10)
    wallet = fields.ForeignKeyField('models.Wallet', related_name='operations', on_delete=fields.CASCADE)

    class Meta:
        table = "operations"
