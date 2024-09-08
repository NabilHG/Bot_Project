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
        investor_profile=1,
        is_admin=True
    )

    user2 = await User.create(
        name="Ana García",
        username="anagarcia",
        phone="987654321",
        investor_profile=2,
        is_admin=False
    )

    user3 = await User.create(
        name="Pepe García",
        username="pepegarcia",
        phone="987654321",
        investor_profile=3,
        is_admin=False
    )

    user4 = await User.create(
        name="Man García",
        username="mangarcia",
        phone="987654321",
        investor_profile=1,
        is_admin=False
    )

    user5 = await User.create(
        name="Won García",
        username="wongarcia",
        phone="987654321",
        investor_profile=1,
        is_admin=False
    )

    user6 = await User.create(
        name="Won2 García",
        username="wongarcia",
        phone="987654321",
        investor_profile=2,
        is_admin=True
    )

    user7 = await User.create(
        name="Won3 García",
        username="wongarcia",
        phone="987654321",
        investor_profile=1,
        is_admin=False
    )

    user8 = await User.create(
        name="Won4 García",
        username="wongarcia",
        phone="987654321",
        investor_profile=3,
        is_admin=False
    )

    user9 = await User.create(
        name="Won5 García",
        username="wongarcia",
        phone="987654321",
        investor_profile=3,
        is_admin=False
    )

    user10 = await User.create(
        name="Won6 García",
        username="wongarcia",
        phone="987654321",
        investor_profile=3,
        is_admin=True
    )

    # Seed Wallets
    wallet1 = await Wallet.create(
        initial_capital=10000.0,
        current_capital=12000.0,
        profit=20.0,
        max_drawdown=23.0,
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
        max_drawdown=3.0,
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

    wallet5 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=5000.0,
        profit=0.0,
        max_drawdown=0.0,
        number_of_operations=0,
        user=user5
    )

    wallet6 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=4000.0,
        profit=-20.0,
        max_drawdown=30.0,
        number_of_operations=56,
        user=user6
    )

    wallet7 = await Wallet.create(
        initial_capital=50000.0,
        current_capital=55000.0,
        profit=5.0,
        max_drawdown=20.0,
        number_of_operations=23,
        user=user7
    )

    wallet8 = await Wallet.create(
        initial_capital=1000.0,
        current_capital=5000.0,
        profit=500.0,
        max_drawdown=60.0,
        number_of_operations=60,
        user=user8
    )

    wallet9 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=11000.0,
        profit=67.0,
        max_drawdown=12.0,
        number_of_operations=12,
        user=user9
    )

    wallet10 = await Wallet.create(
        initial_capital=5000.0,
        current_capital=9000.0,
        profit=45.0,
        max_drawdown=42.0,
        number_of_operations=12,
        user=user10
    )

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
    await WalletShare.create(wallet=wallet6, share=share5)
    await WalletShare.create(wallet=wallet7, share=share6)
    await WalletShare.create(wallet=wallet8, share=share7)

    # Seed Operations
    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=60),
        sell_date=datetime.now() - timedelta(days=30),
        capital_invested=1500.0,
        capital_gained=1600.0,
        status="close",
        wallet=wallet1
    )

    await Operation.create(
        ticker="GOOG",
        buy_date=datetime.now() - timedelta(days=45),
        capital_invested=2000.0,
        status="open",
        wallet=wallet1
    )

    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=120),
        sell_date=datetime.now() - timedelta(days=90),
        capital_invested=3000.0,
        capital_gained=3300.0,
        status="close",
        wallet=wallet3
    )

    await Operation.create(
        ticker="MSFT",
        buy_date=datetime.now() - timedelta(days=75),
        sell_date=datetime.now() - timedelta(days=45),
        capital_invested=1800.0,
        capital_gained=1900.0,
        status="close",
        wallet=wallet3
    )

    await Operation.create(
        ticker="AAPL",
        buy_date=datetime.now() - timedelta(days=180),
        sell_date=datetime.now() - timedelta(days=150),
        capital_invested=3500.0,
        capital_gained=3000.0,
        status="close",
        wallet=wallet4
    )

    await Operation.create(
        ticker="GOOG",
        buy_date=datetime.now() - timedelta(days=100),
        capital_invested=2200.0,
        status="open",
        wallet=wallet4
    )

    await Operation.create(
        ticker="AMZN",
        buy_date=datetime.now() - timedelta(days=150),
        sell_date=datetime.now() - timedelta(days=120),
        capital_invested=2500.0,
        capital_gained=2200.0,
        status="close",
        wallet=wallet4
    )

    await Operation.create(
        ticker="MSFT",
        buy_date=datetime.now() - timedelta(days=90),
        capital_invested=2000.0,
        status="open",
        wallet=wallet4
    )

    await Operation.create(
        ticker="META",
        buy_date=datetime.now() - timedelta(days=30),
        capital_invested=800.0,
        status="open",
        wallet=wallet6
    )

    await Operation.create(
        ticker="BRK-B",
        buy_date=datetime.now() - timedelta(days=50),
        sell_date=datetime.now() - timedelta(days=25),
        capital_invested=1200.0,
        capital_gained=1300.0,
        status="close",
        wallet=wallet7
    )

    await Operation.create(
        ticker="TSM",
        buy_date=datetime.now() - timedelta(days=40),
        capital_invested=1000.0,
        status="open",
        wallet=wallet8
    )

    print("Datos de ejemplo insertados exitosamente.")

    # Cierra la conexión
    await Tortoise.close_connections()