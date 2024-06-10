import asyncio
import logging
import sys
from aiogram import Dispatcher, Router
from bot import api, handlers, config

async def main() -> None:
    bot, dp = await api.init_bot(config.TELEGRAM_BOT_TOKEN)
    
    router = Router()
    handlers.setup_handlers(router)
    
    dp.include_router(router)
    
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