from tortoise import fields
from tortoise.models import Model

class Wallet(Model):
    id = fields.BigIntField(pk=True)
    # initial_capital = fields.FloatField()
    # current_capital = fields.FloatField(null=True)
    # profit = fields.FloatField(null=True)
    # max_drawdown = fields.FloatField(null=True)
    # number_of_operations = fields.IntField(null=True)
    user = fields.ForeignKeyField('models.User', related_name='wallets', on_delete=fields.CASCADE)
    
    class Meta:
        table = "wallets"
