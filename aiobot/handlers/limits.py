from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiobot.utils.menu import (
    build_limits_main_menu,
    build_type_menu,
    build_period_menu,
    build_category_menu,
)
from aiobot.utils.emojis import (
    OK_EMOJI,
    TRANSFER_EMOJI,
    category_emoji,
)
from aiobot.states import SetLimitStates, DeleteLimitStates
from asgiref.sync import sync_to_async
from core.models import Category, CategoryLimit
from django.contrib.auth.models import User

router = Router()

@router.message(Command("limits"))
@router.message(F.text == "🔥 Лимиты")
async def limits_entry(message: types.Message, state: FSMContext):
    """
    Точка входа для управления лимитами: /limits или кнопка "Лимиты" в reply-меню.
    Показывает инлайн-кнопки для действий с лимитами.
    """
    await state.clear()
    await message.answer(
        "Выберите действие с лимитами:",
        reply_markup=build_limits_main_menu()
    )

@router.callback_query(F.data == "set_limit")
async def set_limit_type(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(SetLimitStates.waiting_for_category_type)
    await query.message.edit_text("Для каких категорий хотите задать лимит?", reply_markup=build_type_menu())
    await query.answer()

@router.callback_query(F.data == "limit_type_expense", SetLimitStates.waiting_for_category_type)
@router.callback_query(F.data == "limit_type_income", SetLimitStates.waiting_for_category_type)
async def set_limit_category(query: types.CallbackQuery, state: FSMContext):
    is_income = query.data.endswith("income")
    await state.update_data(is_income=is_income)
    categories = await sync_to_async(list)(Category.objects.filter(is_income=is_income))
    if len(categories) == 0:
        await query.message.edit_text("Нет доступных категорий!", reply_markup=build_limits_main_menu())
        await state.clear()
        return
    menu = await build_category_menu(categories, prefix="setlimit_cat")
    await state.set_state(SetLimitStates.waiting_for_category)
    await query.message.edit_text("Выберите категорию:", reply_markup=menu)
    await query.answer()

@router.callback_query(lambda c: c.data.startswith("setlimit_cat_"), SetLimitStates.waiting_for_category)
async def set_limit_period(query: types.CallbackQuery, state: FSMContext):
    category_id = int(query.data.replace("setlimit_cat_", ""))
    await state.update_data(category_id=category_id)
    await state.set_state(SetLimitStates.waiting_for_period_type)
    await query.message.edit_text("Для какого периода задать лимит?", reply_markup=build_period_menu())
    await query.answer()

@router.callback_query(lambda c: c.data.startswith("period_"), SetLimitStates.waiting_for_period_type)
async def set_limit_amount_entry(query: types.CallbackQuery, state: FSMContext):
    period_type = query.data.replace("period_", "")
    await state.update_data(period_type=period_type)
    await state.set_state(SetLimitStates.waiting_for_amount)
    await query.message.edit_text("Введите лимит (руб.) для выбранной категории и периода:")
    await query.answer()

@router.message(SetLimitStates.waiting_for_amount)
async def set_limit_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(" ", "").replace(",", "."))
        if amount <= 0:
            raise ValueError()
    except Exception:
        await message.answer("Некорректный лимит. Введите положительное число.")
        return
    data = await state.get_data()
    user = await sync_to_async(User.objects.get)(username=str(message.from_user.id))
    category = await sync_to_async(Category.objects.get)(id=data["category_id"])
    period_type = data["period_type"]
    prev_limit = await sync_to_async(CategoryLimit.objects.filter(
        user=user, category=category, period_type=period_type
    ).first)()
    updated = prev_limit is not None
    limit, _ = await sync_to_async(CategoryLimit.objects.update_or_create)(
        user=user, category=category, period_type=period_type, defaults={"amount": amount}
    )
    if updated:
        msg = f"{TRANSFER_EMOJI} Лимит обновлён: {category.name} за {limit.get_period_type_display().lower()} теперь {amount} руб."
    else:
        msg = f"{OK_EMOJI} Лимит установлен для {category.name} на {limit.get_period_type_display().lower()}: {amount} руб."
    await message.answer(msg, reply_markup=build_limits_main_menu())
    await state.clear()

@router.callback_query(F.data == "view_limits")
async def show_limits(query: types.CallbackQuery, state: FSMContext):
    user = await sync_to_async(User.objects.get)(username=str(query.from_user.id))
    limits = await sync_to_async(list)(CategoryLimit.objects.filter(user=user).select_related("category"))
    if not limits:
        await query.message.edit_text("У вас нет активных лимитов.", reply_markup=build_limits_main_menu())
    else:
        blocks = []
        for l in limits:
            ctg_emoji = category_emoji(l.category.name)
            blocks.append(
                f"{ctg_emoji} <b>{l.category.name}</b> ({'доход' if l.category.is_income else 'расход'}) "
                f"— {l.get_period_type_display()}: <b>{l.amount} руб.</b>"
            )
        await query.message.edit_text("Текущие лимиты:\n" + "\n".join(blocks), parse_mode="HTML", reply_markup=build_limits_main_menu())
    await state.clear()
    await query.answer()

@router.callback_query(F.data == "delete_limit")
async def del_limit_type(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(DeleteLimitStates.waiting_for_category_type)
    await query.message.edit_text("Лимит по какой категории удалить?", reply_markup=build_type_menu())
    await query.answer()

@router.callback_query(F.data == "limit_type_expense", DeleteLimitStates.waiting_for_category_type)
@router.callback_query(F.data == "limit_type_income", DeleteLimitStates.waiting_for_category_type)
async def del_limit_category(query: types.CallbackQuery, state: FSMContext):
    is_income = query.data.endswith("income")
    user = await sync_to_async(User.objects.get)(username=str(query.from_user.id))
    limits = await sync_to_async(list)(
        CategoryLimit.objects.filter(user=user, category__is_income=is_income).select_related("category")
    )
    if not limits:
        await query.message.edit_text("Нет лимитов для выбранного типа.", reply_markup=build_limits_main_menu())
        await state.clear()
        return
    categories = [l.category for l in limits]
    menu = await build_category_menu(categories, prefix="dellimit_cat")
    await state.set_state(DeleteLimitStates.waiting_for_category)
    await query.message.edit_text("Выберите категорию:", reply_markup=menu)
    await query.answer()

@router.callback_query(lambda c: c.data.startswith("dellimit_cat_"), DeleteLimitStates.waiting_for_category)
async def del_limit_period(query: types.CallbackQuery, state: FSMContext):
    category_id = int(query.data.replace("dellimit_cat_", ""))
    await state.update_data(category_id=category_id)
    await state.set_state(DeleteLimitStates.waiting_for_period_type)
    await query.message.edit_text("Какой лимит удалить?", reply_markup=build_period_menu())
    await query.answer()

@router.callback_query(lambda c: c.data.startswith("period_"), DeleteLimitStates.waiting_for_period_type)
async def del_limit_confirm(query: types.CallbackQuery, state: FSMContext):
    period_type = query.data.replace("period_", "")
    data = await state.get_data()
    user = await sync_to_async(User.objects.get)(username=str(query.from_user.id))
    category = await sync_to_async(Category.objects.get)(id=data["category_id"])
    limit = await sync_to_async(CategoryLimit.objects.filter(
        user=user, category=category, period_type=period_type
    ).first)()
    if not limit:
        await query.message.edit_text("Лимит не найден для выбранной комбинации.", reply_markup=build_limits_main_menu())
        await state.clear()
        return
    await state.update_data(limit_id=limit.id)
    await state.set_state(DeleteLimitStates.confirming)
    await query.message.edit_text(
        f"Удалить лимит {limit.amount} руб. для «{category.name}» за {limit.get_period_type_display()}?\n"
        "Подтвердите: 'Да' — удалить / 'Нет' — отмена."
    )
    await query.answer()

@router.message(DeleteLimitStates.confirming)
async def del_limit_do(message: types.Message, state: FSMContext):
    if message.text.strip().lower() not in ["да", "yes"]:
        await message.answer("Удаление отменено.", reply_markup=build_limits_main_menu())
        await state.clear()
        return
    data = await state.get_data()
    await sync_to_async(CategoryLimit.objects.filter(id=data["limit_id"]).delete)()
    await message.answer("Лимит удалён.", reply_markup=build_limits_main_menu())
    await state.clear()

@router.callback_query(F.data == "back")
async def limit_back(query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.edit_text("Управление лимитами:", reply_markup=build_limits_main_menu())
    await query.answer()

def register_limit_handlers(dp):
    dp.include_router(router)