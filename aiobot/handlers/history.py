from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("history"))
async def show_history(message: types.Message):
    await message.answer("Этот функционал (история операций) будет реализован на следующем шаге.")

def register_history_handlers(dp):
    dp.include_router(router)
