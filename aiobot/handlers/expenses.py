import django
import os, sys
from aiobot.states import AddExpenseStates
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

    cat_names = [cat.name for cat in categories]
    await state.update_data(category_choices={cat.name: cat.id for cat in categories})
    await state.set_state(AddExpenseStates.waiting_for_category)
    from aiobot.utils.menu import build_categories_menu
    await message.answer(
        "Выберите категорию расхода:",
        reply_markup=build_categories_menu(cat_names)
    )

@router.message(AddExpenseStates.waiting_for_category)
async def add_expense_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category_choices = data.get("category_choices", {})
    cat_num = message.text.strip()
    if cat_num not in category_choices:
        await message.answer("Нет такой категории. Введите номер из списка.")
        return

    await state.update_data(category_id=category_choices[cat_num])
    await state.set_state(AddExpenseStates.waiting_for_date)
    await message.answer("Укажите дату расхода в формате ДД.ММ.ГГГГ (или 'сегодня'):")

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

@router.callback_query(F.data.startswith("category_"), AddExpenseStates.waiting_for_category)
async def callback_expense_category(query: types.CallbackQuery, state: FSMContext):
    cat_name = query.data.replace("category_", "")
    data = await state.get_data()
    category_choices = data.get("category_choices", {})
    category_id = category_choices.get(cat_name)
    if not category_id:
        await query.answer("Ошибка выбора категории.")
        return
    await state.update_data(category_id=category_id)
    await state.set_state(AddExpenseStates.waiting_for_date)
    await query.message.answer("Укажите дату расхода в формате ДД.ММ.ГГГГ (или 'сегодня'):")
    await query.answer()


def register_expense_handlers(dp):
    dp.include_router(router)
