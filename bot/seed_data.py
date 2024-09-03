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

    user3 = await User.create(
        name="Pepe García",
        username="pepegarcia",
        phone="987654321",
        invesestor_profile=3,
        is_admin=False
    )

    user4 = await User.create(
        name="Man García",
        username="mangarcia",
        phone="987654321",
        invesestor_profile=1,
        is_admin=False
    )

    user5 = await User.create(
        name="Won García",
        username="wongarcia",
        phone="987654321",
        invesestor_profile=1,
        is_admin=True
    )

    # Seed Wallets
    wallet1 = await Wallet.create(
        initial_capital=10000.0,
        current_capital=12000.0,
        profit=20.0,
        max_drawdown=-23.0,
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

    wallet3 = await Wallet.create(
        initial_capital=1000.0,
        current_capital=900.0,
        profit=-10.0,
        max_drawdown=-3.0,
        number_of_operations=50,
        user=user3
    )

    wallet4 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=5500.0,
        profit=500.0,
        max_drawdown=3.0,
        number_of_operations=2,
        user=user4
    )

    wallet2 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=5000.0,
        profit=0.0,
        max_drawdown=0.0,
        number_of_operations=0,
        user=user5
    )

    # Seed Shares
    share1 = await Share.create(ticker="AAPL")
    share2 = await Share.create(ticker="GOOG")
    share3 = await Share.create(ticker="META")
    share4 = await Share.create(ticker="IBM")

    # Seed WalletShares
    await WalletShare.create(wallet=wallet1, share=share1)
    await WalletShare.create(wallet=wallet1, share=share2)
    await WalletShare.create(wallet=wallet2, share=share1)
    await WalletShare.create(wallet=wallet3, share=share1)
    await WalletShare.create(wallet=wallet3, share=share4)
    await WalletShare.create(wallet=wallet4, share=share1)
    await WalletShare.create(wallet=wallet4, share=share2)
    await WalletShare.create(wallet=wallet4, share=share3)
    await WalletShare.create(wallet=wallet4, share=share4)

    # Seed Operations
    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=30),
        sell_date=datetime.now() - timedelta(days=15),
        capital_invested=1000.0,
        capital_gained=1100.0,
        status="close",
        wallet=wallet1
    )

    await Operation.create(
        ticker="GOOG",
        buy_date=datetime.now() - timedelta(days=20),
        sell_date=datetime.now() - timedelta(days=10),
        capital_invested=1500.0,
        capital_gained=1700.0,
        status="close",
        wallet=wallet1
    )

    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=25),
        sell_date=datetime.now() - timedelta(days=5),
        capital_invested=500.0,
        capital_gained=600.0,
        status="close",
        wallet=wallet2
    )

    await Operation.create(
        ticker="META",
        buy_date=datetime.now() - timedelta(days=25),
        capital_invested=100.0,
        status="open",
        wallet=wallet3
    )

    await Operation.create(
        ticker="GOOG",
        buy_date=datetime.now() - timedelta(days=5),
        capital_invested=300.0,
        status="open",
        wallet=wallet4
    )



    print("Datos de ejemplo insertados exitosamente.")

    # Cierra la conexión
    await Tortoise.close_connections()