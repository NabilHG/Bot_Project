from tortoise import fields
from tortoise.models import Model

class WalletShare(Model):
    id = fields.IntField(pk=True)
    wallet = fields.ForeignKeyField('models.Wallet', related_name='wallet_share', on_delete=fields.CASCADE)
    share = fields.ForeignKeyField('models.Share', related_name='wallet_share', on_delete=fields.CASCADE)

    class Meta:
        table = "wallet_share"
        unique_together = (('wallet', 'share'),)  # Asegura que una acción solo pueda estar una vez en una cartera