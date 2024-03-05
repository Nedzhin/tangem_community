import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handler import router
import os


async def main():
  bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
  dp = Dispatcher(storage=MemoryStorage())
  dp.include_router(router)

   # Start the polling
  polling_task = dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

  # Wait for the polling task to complete
  await polling_task


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO) 
    asyncio.run(main())