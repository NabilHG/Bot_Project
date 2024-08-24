import asyncio
import logging
import sys
from bot import api, config, data_manager, update_data
from bot.handlers import backtest, info
from dotenv import load_dotenv

load_dotenv()


"""
async def daily_analysis():
    # Lógica para realizar el análisis diario
    # Determina si se deben enviar alertas de compra o venta
    now = datetime.now()
    if now.hour == 10 and now.minute == 0:  # Ejecutar análisis todos los días a las 10:00 AM
        # Ejecutar la lógica de análisis y enviar alertas si es necesario
        await send_buy_sell_alerts()

async def scurrent_api_key_indexend_buy_sell_alerts():
    # Lógica para enviar alertas de compra y venta
    # Por ejemplo:
    # await bot.send_message(chat_id, "¡Alerta de compra!")
    # await bot.send_message(chat_id, "¡Alerta de venta!")

# Agregar el handler para el análisis diario
async def start_analysis_scheduler():
    while True:
        await daily_analysis()
        # Esperar 24 horas antes de ejecutar el análisis nuevamente
        await asyncio.sleep(24 * 60 * 60)
"""

async def update_data_task():
    while True:
        await update_data.update_data()
        await asyncio.sleep(5)

updated_data = False

async def main() -> None:
    updated_data = False

    # asyncio.create_task(update_data_task())
    updated_data = await update_data.update_data(updated_data)
    print(f'Updated data: {updated_data}')
    updated_data = await update_data.update_data(updated_data)
    print(f'Updated data: {updated_data}')
    
    bot, dp = await api.init_bot(config.TELEGRAM_BOT_TOKEN)
    """
    # Iniciar el análisis diario en un hilo separado
    analysis_task = asyncio.create_task(start_analysis_scheduler())
    """
    # await data_manager.get_data()

    dp.include_router(backtest.router)
    dp.include_router(info.router)

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