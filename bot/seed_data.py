from tortoise import Tortoise
from bot.db.models import User, Wallet, Operation, Share, WalletShare
from datetime import datetime, timedelta
from bot.config import TORTOISE_ORM

async def seed_data():
    # Conecta la base de datos
    await Tortoise.init(TORTOISE_ORM)
    
    # Borra y recrea las tablas (opcional, útil para reiniciar los datos)
    await Tortoise.generate_schemas(safe=True)

    
    # Seed Shares
    share1 = await Share.create(ticker="AAPL")
    share2 = await Share.create(ticker="GOOG")
    share3 = await Share.create(ticker="AMZN")
    share4 = await Share.create(ticker="MSFT")
    share5 = await Share.create(ticker="META")
    share6 = await Share.create(ticker="BRK-B")
    share7 = await Share.create(ticker="TSM")
    share8 = await Share.create(ticker="ASML")
    share9 = await Share.create(ticker="TSLA")
    share10 = await Share.create(ticker="BABA")
    share11 = await Share.create(ticker="JPM")
    share12 = await Share.create(ticker="V")
    share13 = await Share.create(ticker="MA")
    share14 = await Share.create(ticker="UNH")
    share15 = await Share.create(ticker="HD")

    

    
    print("Shares insertados exitosamente.")

    # Cierra la conexión
    await Tortoise.close_connections()