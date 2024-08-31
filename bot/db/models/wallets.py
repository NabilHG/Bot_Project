from tortoise import fields
from tortoise.models import Model

class Wallet(Model):
    id = fields.IntField(pk=True)
    initial_capital = fields.FloatField()
    current_capital = fields.FloatField()
    profit = fields.FloatField()
    max_drawdown = fields.FloatField()
    number_of_operations = fields.IntField()
    user = fields.ForeignKeyField('models.User', related_name='wallets', on_delete=fields.CASCADE)
    
    class Meta:
        table = "wallets"
