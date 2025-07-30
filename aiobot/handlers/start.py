from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from aiobot.utils.messages import get_message
from aiobot.utils.menu import main_menu
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """
    Приветствие и стартовое меню — регистрация пользователя, reply-клавиатура.
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    user_obj, created = await sync_to_async(User.objects.get_or_create)(
        username=str(user_id),
        defaults={"first_name": first_name}
    )
    greeting = get_message("registered") if created else get_message("start")
    await message.answer(
        f"{greeting}\nИспользуйте главное меню для работы:",
        reply_markup=main_menu
    )
    await state.clear()


# Главная reply-клавиатура — выбираются кнопки, НЕ команды!
@router.message(F.text == "Добавить расход")
async def menu_add_expense(message: types.Message, state: FSMContext):
    from aiobot.handlers.expenses import start_add_expense
    await state.clear()
    await start_add_expense(message, state)

@router.message(F.text == "Добавить доход")
async def menu_add_income(message: types.Message, state: FSMContext):
    from aiobot.handlers.income import start_add_income
    await state.clear()
    await start_add_income(message, state)

@router.message(F.text == "История операций")
async def menu_history(message: types.Message, state: FSMContext):
    from aiobot.handlers.history import history_scope
    await state.clear()
    await history_scope(message, state)

@router.message(F.text == "Статистика")
async def menu_summary(message: types.Message, state: FSMContext):
    from aiobot.handlers.summary import summary_start
    await state.clear()
    await summary_start(message, state)

@router.message(F.text == "Лимиты")
async def menu_limits(message: types.Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Установить лимит"), types.KeyboardButton(text="Удалить лимит")],
            [types.KeyboardButton(text="Назад в меню")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Выберите действие с лимитами:", reply_markup=kb)

@router.message(F.text == "Установить лимит")
async def menu_set_limit(message: types.Message, state: FSMContext):
    from aiobot.handlers.setlimit import start_setlimit
    await state.clear()
    await start_setlimit(message, state)

@router.message(F.text == "Удалить лимит")
async def menu_del_limit(message: types.Message, state: FSMContext):
    from aiobot.handlers.deletelimit import start_del_limit
    await state.clear()
    await start_del_limit(message, state)

@router.message(F.text == "Назад в меню")
async def menu_back(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(get_message("main_menu"), reply_markup=main_menu)

def register_start_handlers(dp):
    dp.include_router(router)
