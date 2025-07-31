from aiobot.states import DeleteLimitStates
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from core.models import Category, CategoryLimit

router = Router()

@router.message(Command("dellimit"))
async def start_del_limit(message: types.Message, state: FSMContext):
    await state.set_state(DeleteLimitStates.waiting_for_category_type)
    await message.answer("Лимит по какой категории удалить?\n1. Расходные\n2. Доходные\nВыберите цифру:")

@router.message(DeleteLimitStates.waiting_for_category_type)
async def del_limit_cat_type(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    if choice not in ("1", "2"):
        await message.answer("Пожалуйста, введите 1 (расходные) или 2 (доходные).")
        return
    is_income = choice == "2"
    categories = await sync_to_async(list)(Category.objects.filter(is_income=is_income))
    if not categories:
        await message.answer("Для этого типа категорий лимитов нет.")
        await state.clear()
        return
    from aiobot.utils.menu import build_category_menu
    category_buttons = [(cat.name, f"catid_{cat.id}") for cat in categories]
    await state.update_data(is_income=is_income, category_choices={f"catid_{cat.id}": cat.id for cat in categories})
    await state.set_state(DeleteLimitStates.waiting_for_category)
    menu = await build_category_menu(category_buttons)
    await message.answer("Выберите категорию:", reply_markup=menu)

@router.callback_query(lambda c: c.data.startswith("catid_"), DeleteLimitStates.waiting_for_category)
async def del_limit_category_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_choices"][query.data]
    await state.update_data(category_id=category_id)
    await state.set_state(DeleteLimitStates.waiting_for_period_type)
    await query.message.answer("Какой лимит удалить?\n1. День\n2. Месяц\n3. Год\nВведите цифру:")
    await query.answer()

@router.message(DeleteLimitStates.waiting_for_period_type)
async def del_limit_period(message: types.Message, state: FSMContext):
    periods = {"1": "day", "2": "month", "3": "year"}
    choice = message.text.strip()
    if choice not in periods:
        await message.answer("Выберите: 1 (день), 2 (месяц), 3 (год).")
        return
    await state.update_data(period_type=periods[choice])
    data = await state.get_data()
    user = await sync_to_async(User.objects.get)(username=str(message.from_user.id))
    category = await sync_to_async(Category.objects.get)(id=data["category_id"])
    limit = await sync_to_async(CategoryLimit.objects.filter(
        user=user, category=category, period_type=periods[choice]).first)()
    if not limit:
        await message.answer("Для этой категории и периода лимит не найден.")
        await state.clear()
        return
    await state.update_data(limit_id=limit.id)
    await state.set_state(DeleteLimitStates.confirming)
    await message.answer(
        f"Точно удалить лимит {limit.amount} руб. для «{category.name}» за {limit.get_period_type_display().lower()}?\n"
        f"Напишите 'да' для удаления или 'отмена' для выхода."
    )

@router.message(DeleteLimitStates.confirming)
async def del_limit_confirm(message: types.Message, state: FSMContext):
    text = message.text.strip().lower()
    if text != 'да':
        await message.answer("Удаление отменено.")
        await state.clear()
        return
    data = await state.get_data()
    await sync_to_async(CategoryLimit.objects.filter(id=data["limit_id"]).delete)()
    await message.answer("Лимит удалён ✅")
    await state.clear()

@router.message(lambda msg: msg.text and msg.text.lower() == "отмена")
async def cancel_del_limit(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Операция по удалению лимита отменена.")

def register_del_limit_handlers(dp):
    dp.include_router(router)
