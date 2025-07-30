"""
Асинхронные универсальные диалоговые функции для FSM-сценариев Telegram-бота.
SOLID, поддержка aiogram FSM, вынесение повторов!
"""

from aiogram.fsm.context import FSMContext
from aiogram import types

from .menu import build_period_menu, build_categories_menu

async def ask_for_period(
    message: types.Message,
    state: FSMContext,
    next_state
) -> None:
    """
    Запросить у пользователя выбор периода через инлайн-меню.
    """
    await state.set_state(next_state)
    await message.answer("Выберите период:", reply_markup=build_period_menu())

async def ask_for_category(
    message: types.Message,
    state: FSMContext,
    categories: list[str],
    next_state
) -> None:
    """
    Запросить у пользователя категорию через инлайн-меню.
    """
    await state.set_state(next_state)
    await message.answer(
        "Выберите категорию:",
        reply_markup=build_categories_menu(categories)
    )

async def cancel_handler(
    message: types.Message,
    state: FSMContext,
    text: str = "Ввод отменён."
) -> None:
    """
    Универсальный обработчик отмены любого сценария.
    """
    await state.clear()
    await message.answer(text)
