from tortoise import fields
from tortoise.models import Model
from .wallets import Wallet  # Importa Cartera para las relaciones

class Operation(Model):
    id = fields.IntField(pk=True)
    date = fields.DatetimeField(auto_now_add=True)
    # more fields here
    wallet = fields.ForeignKeyField('models.Wallet', related_name='operations', on_delete=fields.CASCADE)

    class Meta:
        table = "operations"
