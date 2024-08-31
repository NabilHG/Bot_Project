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
    