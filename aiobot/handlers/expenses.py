import django
import os, sys
from aiobot.states import AddExpenseStates
from aiobot.utils.emojis import EXPENSE_EMOJI
from aiobot.utils.menu import build_category_menu
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from core.models import Transaction, Category
from datetime import datetime, date
from django.contrib.auth.models import User


# --- Django ORM подключаем ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")

django.setup()

router = Router()

@router.message(F.text.casefold() == "отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод отменён.")

@router.message(Command("add_expense"))
@router.message(F.text == f"{EXPENSE_EMOJI} Добавить расход")
async def start_add_expense(message: types.Message, state: FSMContext):
    await state.set_state(AddExpenseStates.waiting_for_amount)
    await message.answer("Введите сумму расхода:")

@router.message(AddExpenseStates.waiting_for_amount)
async def add_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 250.75).")
        return

    categories = await sync_to_async(list)(Category.objects.filter(is_income=False))
    if not categories:
        await message.answer("Категории расходов ещё не созданы. Добавьте категории через админ-панель Django.")
        await state.clear()
        return

    categories = await sync_to_async(list)(Category.objects.filter(is_income=False))
    if not categories:
        await message.answer("Категории расходов ещё не созданы.")
        await state.clear()
        return

    await state.set_state(AddExpenseStates.waiting_for_category)
    menu = build_category_menu(categories, prefix="expense_cat")
    await message.answer("Выберите категорию расхода:", reply_markup=menu)

@router.callback_query(lambda c: c.data.startswith("expense_cat_"), AddExpenseStates.waiting_for_category)
async def callback_expense_category(query: types.CallbackQuery, state: FSMContext):
    category_id = int(query.data.replace("expense_cat_", ""))
    await state.update_data(category_id=category_id)
    await state.set_state(AddExpenseStates.waiting_for_date)
    await query.message.answer("Укажите дату расхода в формате ДД.ММ.ГГГГ (или 'сегодня'):")
    await query.answer()

@router.message(AddExpenseStates.waiting_for_date)
async def add_expense_date(message: types.Message, state: FSMContext):
    text = message.text.lower().strip()
    if text in ["сегодня", "today"]:
        dt = date.today()
    else:
        try:
            dt = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer("Некорректная дата. Пример: 21.07.2025 или 'сегодня'.")
            return
    await state.update_data(date=dt)
    await state.set_state(AddExpenseStates.waiting_for_description)
    await message.answer("Введите описание (или '-' если оставить пустым):")

@router.message(AddExpenseStates.waiting_for_description)
async def add_expense_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    description = "" if message.text.strip() == "-" else message.text.strip()
    user = message.from_user
    user_id = user.id

    try:
        user_obj, _ = await sync_to_async(User.objects.get_or_create)(
            username=str(user_id),
            defaults={"first_name": user.first_name or ""}
        )
        category = await sync_to_async(Category.objects.get)(
            id=data["category_id"], is_income=False
        )
        await sync_to_async(Transaction.objects.create)(
            user=user_obj,
            category=category,
            amount=data["amount"],
            date=data["date"],
            description=description
        )
        await message.answer("Расход успешно добавлен!")
    except Exception as e:
        await message.answer(f"Ошибка добавления расхода: {e}")
    finally:
        await state.clear()

def register_expense_handlers(dp):
    dp.include_router(router)
