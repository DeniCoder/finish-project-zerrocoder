import django
import os, sys
from aiobot.states import AddIncomeStates
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from core.models import Transaction, Category
from django.contrib.auth.models import User

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")

django.setup()

router = Router()

@router.message(F.text.casefold() == "отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод отменён.")

@router.message(Command("add_income"))
async def start_add_income(message: types.Message, state: FSMContext):
    await state.set_state(AddIncomeStates.waiting_for_amount)
    await message.answer("Введите сумму дохода:")

@router.message(AddIncomeStates.waiting_for_amount)
async def add_income_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 5000.00).")
        return

    categories = await sync_to_async(list)(Category.objects.filter(is_income=True))
    if not categories:
        await message.answer("Категории доходов ещё не созданы. Добавьте их через админ-панель Django.")
        await state.clear()
        return

    num_to_id = {str(i+1): cat.id for i, cat in enumerate(categories)}
    cat_lines = [f"{i+1}. {cat.name}" for i, cat in enumerate(categories)]
    await state.update_data(category_choices=num_to_id)
    await state.set_state(AddIncomeStates.waiting_for_category)
    await message.answer("Выберите категорию (цифра):\n" + "\n".join(cat_lines))

@router.message(AddIncomeStates.waiting_for_category)
async def add_income_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    category_choices = data.get("category_choices", {})
    cat_num = message.text.strip()
    if cat_num not in category_choices:
        await message.answer("Нет такой категории. Введите номер из списка.")
        return

    await state.update_data(category_id=category_choices[cat_num])
    await state.set_state(AddIncomeStates.waiting_for_date)
    await message.answer("Укажите дату дохода в формате ДД.ММ.ГГГГ (или 'сегодня'):")

@router.message(AddIncomeStates.waiting_for_date)
async def add_income_date(message: types.Message, state: FSMContext):
    from datetime import datetime, date
    text = message.text.lower().strip()
    if text in ["сегодня", "today"]:
        dt = date.today()
    else:
        try:
            dt = datetime.strptime(text, "%d.%m.%Y").date()
        except ValueError:
            await message.answer("Некорректная дата. Пример: 20.03.2025 или 'сегодня'.")
            return
    await state.update_data(date=dt)
    await state.set_state(AddIncomeStates.waiting_for_description)
    await message.answer("Введите описание (или '-' если пусто):")

@router.message(AddIncomeStates.waiting_for_description)
async def add_income_description(message: types.Message, state: FSMContext):
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
            id=data["category_id"], is_income=True
        )
        await sync_to_async(Transaction.objects.create)(
            user=user_obj,
            category=category,
            amount=data["amount"],
            date=data["date"],
            description=description
        )
        await message.answer("Доход успешно добавлен!")
    except Exception as e:
        await message.answer(f"Ошибка добавления дохода: {e}")
    finally:
        await state.clear()

def register_income_handlers(dp):
    dp.include_router(router)
