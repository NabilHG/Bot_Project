from tortoise import fields
from tortoise.models import Model
from .users import User  # Importa Usuario para las relaciones

class Wallet(Model):
    id = fields.IntField(pk=True)
    # more fields here
    usuario = fields.ForeignKeyField('models.User', related_name='wallets', on_delete=fields.CASCADE)
    class Meta:
        table = "wallets"
