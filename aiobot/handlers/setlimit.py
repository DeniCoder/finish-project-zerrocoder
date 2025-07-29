from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiobot.states import SetLimitStates
from aiobot.utils.formatting import format_rub
from asgiref.sync import sync_to_async

router = Router()

@router.message(F.text.casefold() == "отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод лимита отменён.")

@router.message(Command("setlimit"))
async def start_setlimit(message: types.Message, state: FSMContext):
    await state.set_state(SetLimitStates.waiting_for_category_type)
    await message.answer("Для каких категорий вы хотите задать лимит?\n1. Расходные\n2. Доходные\nВыберите цифру:")

@router.message(SetLimitStates.waiting_for_category_type)
async def setlimit_category_type(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    if choice not in ("1", "2"):
        await message.answer("Пожалуйста, введите 1 (расходные) или 2 (доходные).")
        return
    is_income = choice == "2"
    from core.models import Category
    categories = await sync_to_async(list)(Category.objects.filter(is_income=is_income))
    if not categories:
        await message.answer("Нет категорий выбранного типа.")
        await state.clear()
        return
    num_to_id = {str(i+1): cat.id for i, cat in enumerate(categories)}
    lines = [f"{i+1}. {cat.name}" for i, cat in enumerate(categories)]
    await state.update_data(is_income=is_income, category_choices=num_to_id)
    await state.set_state(SetLimitStates.waiting_for_category)
    await message.answer("Выберите номер категории:\n" + "\n".join(lines))

@router.message(SetLimitStates.waiting_for_category)
async def setlimit_category_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    num = message.text.strip()
    category_choices = data["category_choices"]
    if num not in category_choices:
        await message.answer("Нет такой категории. Попробуйте еще раз.")
        return
    await state.update_data(category_id=category_choices[num])
    await state.set_state(SetLimitStates.waiting_for_period_type)
    await message.answer("Для какого периода задать лимит?\n1. День\n2. Месяц\n3. Год\nВыберите цифру:")

@router.message(SetLimitStates.waiting_for_period_type)
async def setlimit_period_select(message: types.Message, state: FSMContext):
    periods = {"1": "day", "2": "month", "3": "year"}
    choice = message.text.strip()
    if choice not in periods:
        await message.answer("Выберите: 1 (день), 2 (месяц), 3 (год)")
        return
    await state.update_data(period_type=periods[choice])
    await state.set_state(SetLimitStates.waiting_for_amount)
    await message.answer("Введите лимит (руб.) для выбранной категории и периода:")

@router.message(SetLimitStates.waiting_for_amount)
async def setlimit_amount(message: types.Message, state: FSMContext):
    from core.models import Category, CategoryLimit
    from django.contrib.auth.models import User
    data = await state.get_data()
    try:
        amount = float(message.text.replace(' ', '').replace(',', '.'))
        if amount <= 0:
            raise ValueError()
    except Exception:
        await message.answer("Некорректный лимит. Введите положительное число.")
        return
    user = await sync_to_async(User.objects.get)(username=str(message.from_user.id))
    category = await sync_to_async(Category.objects.get)(id=data["category_id"])
    period_type = data["period_type"]
    # Проверяем, есть ли уже лимит для данной связки
    prev_limit = await sync_to_async(CategoryLimit.objects.filter(
        user=user, category=category, period_type=period_type
    ).first)()
    updated = prev_limit is not None
    limit, _ = await sync_to_async(CategoryLimit.objects.update_or_create)(
        user=user, category=category, period_type=period_type, defaults={"amount": amount})
    if updated:
        await message.answer(
            f"🔄 Лимит по категории «{category.name}» за {limit.get_period_type_display().lower()} обновлён: "
            f"было {format_rub(prev_limit.amount)} руб., стало {format_rub(amount)} руб."
        )
    else:
        await message.answer(
            f"✅ Лимит {format_rub(amount)} руб. установлен для категории «{category.name}» за {limit.get_period_type_display().lower()}."
        )
    await state.clear()

def register_setlimit_handlers(dp):
    dp.include_router(router)
