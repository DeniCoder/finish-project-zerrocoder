import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.expenses import register_expense_handlers
from handlers.income import register_income_handlers
from handlers.history import register_history_handlers
from handlers.summary import register_summary_handlers
from handlers.charts import register_chart_handlers

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем все обработчики
register_expense_handlers(dp)
register_income_handlers(dp)
register_history_handlers(dp)
register_summary_handlers(dp)
register_chart_handlers(dp)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
