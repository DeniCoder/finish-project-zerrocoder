from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiobot.states import CategoryStatsStates
from datetime import date, datetime
import os, sys
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()
from core.models import Transaction, Category

router = Router()

WEEKDAYS_RU = {
    0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'
}

@router.message(Command("category"))
async def start_category_dialog(message: types.Message, state: FSMContext):
    # Сначала спросим: расход или доход
    await state.set_state(CategoryStatsStates.waiting_for_type)
    await message.answer("Показать операции по:\n1. Расходным категориям\n2. Доходным категориям\n\nОтветьте цифрой: 1 или 2")

@router.message(CategoryStatsStates.waiting_for_type)
async def category_type_selected(message: types.Message, state: FSMContext):
    answer = message.text.strip()
    if answer not in ("1", "2"):
        await message.answer("Пожалуйста, введите 1 (расходы) или 2 (доходы).")
        return
    is_income = True if answer == "2" else False
    # Получаем категории по типу
    categories = await sync_to_async(list)(Category.objects.filter(is_income=is_income))
    if not categories:
        await message.answer("Нет категорий выбранного типа.")
        await state.clear()
        return
    # Сохраняем тип и сопоставление в настройки FSM
    num_to_id = {str(i+1): cat.id for i, cat in enumerate(categories)}
    cat_lines = [f"{i+1}. {cat.name}" for i, cat in enumerate(categories)]
    await state.update_data(is_income=is_income, category_choices=num_to_id)
    await state.set_state(CategoryStatsStates.waiting_for_category)
    await message.answer("Выберите категорию (номер):\n" + "\n".join(cat_lines))

@router.message(CategoryStatsStates.waiting_for_category)
async def category_selected(message: types.Message, state: FSMContext):
    data = await state.get_data()
    is_income = data["is_income"]
    category_choices = data["category_choices"]
    num = message.text.strip()
    if num not in category_choices:
        await message.answer("Нет такой категории. Попробуйте ввести номер из списка.")
        return
    category_id = category_choices[num]
    # Получаем пользователя и данные
    user_id = message.from_user.id
    from django.contrib.auth.models import User
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Вы ещё не добавляли ни одной операции.")
        await state.clear()
        return

    today = date.today()
    start_of_month = date(today.year, today.month, 1)
    category = await sync_to_async(Category.objects.get)(id=category_id)

    transactions = await sync_to_async(list)(
        Transaction.objects
            .filter(user=user_obj, category=category, date__gte=start_of_month, date__lte=today)
            .select_related('category')
            .order_by('date', '-id')
    )

    if not transactions:
        await message.answer("За этот месяц в выбранной категории ещё не было записей.")
        await state.clear()
        return

    # Группируем по дням
    grouped = dict()
    for t in transactions:
        d = t.date
        if d not in grouped:
            grouped[d] = []
        sign = '+' if t.category.is_income else '-'
        grouped[d].append(
            f"{sign}{t.amount} | {t.description or '-'}"
        )
    lines = [f"Операции за месяц по категории: {category.name}"]
    day_keys = sorted(grouped.keys())
    for d in day_keys:
        weekday = WEEKDAYS_RU[d.weekday()]
        day_head = f"{weekday} {d.strftime('%d.%m.%Y')}:"
        lines.append(day_head)
        for op_str in grouped[d]:
            lines.append(op_str)
    sum_by_cat = sum(float(t.amount) for t in transactions)
    label = "Сумма дохода" if is_income else "Сумма расхода"
    lines.append(f"\n{label}: {sum_by_cat}")
    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    lines.append(f"Время получения информации: {now}")

    await message.answer("\n".join(lines))
    await state.clear()

def register_history_category_handlers(dp):
    dp.include_router(router)
