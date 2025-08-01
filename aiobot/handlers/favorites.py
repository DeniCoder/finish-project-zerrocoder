from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("favorites"))
async def show_favorites(message: types.Message):
    await message.answer("Избранные отчёты пока не реализованы. В будущем здесь появится список ваших избранных аналитик и отчётов.")

@router.message(Command("add_favorite"))
async def add_favorite(message: types.Message):
    await message.answer("Добавление в избранное пока не реализовано. В будущем вы сможете сохранять отчёты в избранное одной командой.")