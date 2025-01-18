from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError
from bot.config import TORTOISE_ORM


async def init_db():
    try:
        # Intentamos inicializar la conexión
        await Tortoise.init(TORTOISE_ORM)
        # Comprobamos si las tablas ya existen
        await Tortoise.generate_schemas(safe=True)  # `safe=True` no eliminará las tablas existentes, solo creará las faltantes
        print("La base de datos ha sido conectada e inicializada correctamente.")
        
    except DBConnectionError as e:
        print(f"Error al conectar con la base de datos: {e}")
        raise

async def close_db():
    await Tortoise.close_connections()

async def test_db_connection():
    try:
        print("Probar conexión...")
        await Tortoise.init(TORTOISE_ORM)
        print("Conexión exitosa.")
        await Tortoise.close_connections()
    except Exception as e:
        print(f"Error al conectar: {e}")