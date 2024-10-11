import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import callback_query

from config_data.config import Config, load_config
from handlers import user_handlers, story_handlers, answer_reports, admins_handlers
from handlers import pay


# Password MySQL: KsC6(n@:AM$/^0E
logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Бот запущен...')

    config: Config = load_config()

    storage = MemoryStorage()
    bot = Bot(
        token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    dp.include_router(pay.router)
    dp.include_router(answer_reports.router)
    dp.include_router(admins_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(story_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

asyncio.run(main())
