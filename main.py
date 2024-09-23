import asyncio
import logging
import sys
from aiogram.types import Message, BotCommand
from bot import api, config, data_manager, update_data, analysis, seed_data
from datetime import datetime, time, timedelta
from aiogram import Router
from bot.db import init_db

router = Router()

async def wait_until(target_time: time):
    """Espera hasta que el reloj alcance la hora objetivo."""
    now = datetime.now()
    target_datetime = datetime.combine(now.date(), target_time)
    if target_datetime < now:
        target_datetime += timedelta(days=1)
    wait_seconds = (target_datetime - now).total_seconds()
    print(f'We are going to wait: {wait_seconds} seconds')
    await asyncio.sleep(wait_seconds)

async def update_data_task(updated_data, is_ticker_updated):
    print(f'Updated data: {updated_data[0]}')
    while not updated_data[0]:
        print(f'While loop updated_data: {updated_data[0]}')
        await update_data.update_data(updated_data, is_ticker_updated)
        await asyncio.sleep(5)
    print("exit")
    
    return updated_data

async def analysis_task(bot):
    print("Analysis here")
    await analysis.analysis(bot)



async def schedule_daily_task(updated_data, is_ticker_updated, bot):
    """Programa la actualización diaria a las 22:30."""
    while True:
        await wait_until(time(22, 30))  # Espera hasta las 22:30
        print("Starting data update...")

        # Ejecuta la actualización sin bloquear otras tareas
        update_data = await update_data_task(updated_data, is_ticker_updated)
        print(f'Updated all data: {update_data}')
        if update_data:
            await analysis_task(bot)
        # Resetea el estado para la próxima actualización diaria
        updated_data[0] = False
        is_ticker_updated = {ticker: False for ticker in config.MATRIX[list(config.MATRIX.keys())[-1]]}


def is_analysis_time():
    # Verifica si estamos en el periodo de analisis (22:25 - 22:40)
    now = datetime.now().time()
    maintenance_start = time(22, 29)
    maintenance_end = time(22, 35)
    return maintenance_start <= now <= maintenance_end

#Handler específico solo para tiempos de mantenimiento
@router.message(lambda message: is_analysis_time())  # Se registra solo para tiempos de mantenimiento
async def handle_maintenance_message(message: Message):
    print("OYE1")
    await message.reply("🚧 Mientras se hace el análisis diario el bot no puede recibir mensajes. Por favor, inténtalo a partir de las 22:35. 🚧")

async def set_commands(bot):
    commands = [
        BotCommand(command="/info", description="obtener más información"),
        BotCommand(command="/perfil", description="ver el perfil actualizado"),
        BotCommand(command="/actualizar", description="para editar ciertas características de tu perfil"),
        BotCommand(command="/generar_link", description="genera un link para poder invitar a raiz de tu cuenta"),
        BotCommand(command="/comprar", description="debes de proporcionar el ticker concreto para registrar una compra"),
        BotCommand(command="/vender", description="debes de proporcionar el ticker concreto para registrar una venta"),
    ]
    await bot.set_my_commands(commands)

async def main() -> None:

    bot, dp = await api.init_bot(config.TELEGRAM_BOT_TOKEN)
    await api.init_routers(dp)
    await set_commands(bot)
    # Inicializa la base de datos
    # await init_db() 

    #Seed data base
    # await seed_data.seed_data()
    
    updated_data = [False]
    is_ticker_updated = {ticker: False for ticker in config.MATRIX[list(config.MATRIX.keys())[-1]]}

    # Inicia la tarea diaria
    asyncio.create_task(schedule_daily_task(updated_data, is_ticker_updated, bot))
        


    # await data_manager.get_data()



    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped.")