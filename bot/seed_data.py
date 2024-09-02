from tortoise import Tortoise
from bot.db.models import User, Wallet, Operation, Share, WalletShare
from datetime import datetime, timedelta
from bot.config import TORTOISE_ORM

async def seed_data():
    # Conecta la base de datos
    await Tortoise.init(TORTOISE_ORM)
    
    # Borra y recrea las tablas (opcional, útil para reiniciar los datos)
    await Tortoise.generate_schemas(safe=True)

    # Seed Users
    user1 = await User.create(
        name="Juan Pérez",
        username="juanperez",
        phone="123456789",
        invesestor_profile=1,
        is_admin=True
    )
    user2 = await User.create(
        name="Ana García",
        username="anagarcia",
        phone="987654321",
        invesestor_profile=2,
        is_admin=False
    )

    # Seed Wallets
    wallet1 = await Wallet.create(
        initial_capital=10000.0,
        current_capital=12000.0,
        profit=2000.0,
        max_drawdown=5.0,
        number_of_operations=10,
        user=user1
    )
    
    wallet2 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=5500.0,
        profit=500.0,
        max_drawdown=3.0,
        number_of_operations=5,
        user=user2
    )

    # Seed Shares
    share1 = await Share.create(ticker="AAPL")
    share2 = await Share.create(ticker="GOOG")

    # Seed WalletShares
    await WalletShare.create(wallet=wallet1, share=share1)
    await WalletShare.create(wallet=wallet1, share=share2)
    await WalletShare.create(wallet=wallet2, share=share1)

    # Seed Operations
    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=30),
        sell_date=datetime.now() - timedelta(days=15),
        capital_invested=1000.0,
        capital_gained=1100.0,
        wallet=wallet1
    )

    await Operation.create(
        ticker="GOOG",
        buy_date=datetime.now() - timedelta(days=20),
        sell_date=datetime.now() - timedelta(days=10),
        capital_invested=1500.0,
        capital_gained=1700.0,
        wallet=wallet1
    )

    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=25),
        sell_date=datetime.now() - timedelta(days=5),
        capital_invested=500.0,
        capital_gained=600.0,
        wallet=wallet2
    )

    print("Datos de ejemplo insertados exitosamente.")

    # Cierra la conexión
    await Tortoise.close_connections()