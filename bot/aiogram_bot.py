import os
from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Загружаем переменные из .env
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Бот работает на aiogram.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
py