"""
Выводит отчет об операциях за произвольный период,
добавляет в отчет предупреждения о превышении лимита и аномальных тратах.
"""

from aiobot.states import HistoryStates
from aiobot.utils.anomalies import detect_anomalies, check_limit_exceed
from aiobot.utils.datetime_formats import WEEKDAYS_RU
from aiobot.utils.formatting import format_rub
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from core.models import Transaction, Category
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User

router = Router()

@router.message(F.text.casefold() == "отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод отменён.")

@router.message(Command("history"))
async def history_scope(message: types.Message, state: FSMContext):
    await state.set_state(HistoryStates.waiting_for_scope)
    await message.answer(
        "Вы хотите посмотреть историю по всем категориям или по какой-то конкретной?\n"
        "1. Все категории\n"
        "2. Конкретная категория\n"
        "Напишите цифру:"
    )

@router.message(HistoryStates.waiting_for_scope)
async def history_scope_choice(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    if choice == "1":
        await state.update_data(scope="all")
        await ask_period(message, state)
    elif choice == "2":
        await state.update_data(scope="category")
        await state.set_state(HistoryStates.waiting_for_category_type)
        await message.answer(
            "По какому типу категорий показать?\n1. Расходные\n2. Доходные\nОтветьте цифрой:"
        )
    else:
        await message.answer("Пожалуйста, введите 1 (все категории) или 2 (конкретная категория).")

@router.message(HistoryStates.waiting_for_category_type)
async def history_category_type(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    if choice not in ("1", "2"):
        await message.answer("Пожалуйста, введите 1 (расходные) или 2 (доходные).")
        return
    is_income = choice == "2"
    await state.update_data(is_income=is_income)

    categories = await sync_to_async(list)(Category.objects.filter(is_income=is_income))
    if not categories:
        await message.answer("Нет категорий выбранного типа.")
        await state.clear()
        return
    from aiobot.utils.menu import build_category_menu
    category_buttons = [(cat.name, f"catid_{cat.id}") for cat in categories]
    await state.update_data(category_choices={f"catid_{cat.id}": cat.id for cat in categories})
    await state.set_state(HistoryStates.waiting_for_category)
    menu = await build_category_menu(category_buttons)
    await message.answer("Выберите категорию:", reply_markup=menu)

@router.callback_query(lambda c: c.data.startswith("catid_"), HistoryStates.waiting_for_category)
async def history_category_callback(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data["category_choices"][query.data]
    await state.update_data(category_id=category_id)
    await ask_period(query.message, state)
    await query.answer()

async def ask_period(message, state):
    await state.set_state(HistoryStates.waiting_for_period_type)
    await message.answer(
        "Выберите период:\n"
        "1. Один день\n"
        "2. Диапазон дат\n"
        "3. Месяц\n"
        "4. Год\nВведите цифру:"
    )

@router.message(HistoryStates.waiting_for_period_type)
async def history_period_choose(message: types.Message, state: FSMContext):
    periods = {"1": "day", "2": "range", "3": "month", "4": "year"}
    choice = message.text.strip()
    if choice not in periods:
        await message.answer("Пожалуйста, выберите: 1 (день), 2 (диапазон дат), 3 (месяц), 4 (год).")
        return
    period_type = periods[choice]
    await state.update_data(period_type=period_type)
    if period_type == "day":
        await state.set_state(HistoryStates.waiting_for_day)
        await message.answer("Введите дату: ДД.ММ.ГГГГ (например, 22.07.2025)")
    elif period_type == "range":
        await state.set_state(HistoryStates.waiting_for_range)
        await message.answer("Введите диапазон: ДД.ММ.ГГГГ-ДД.ММ.ГГГГ")
    elif period_type == "month":
        await state.set_state(HistoryStates.waiting_for_month)
        await message.answer("Месяц и год: ММ.ГГГГ (например, 07.2025)")
    elif period_type == "year":
        await state.set_state(HistoryStates.waiting_for_year)
        await message.answer("Год: ГГГГ (например, 2025)")

@router.message(HistoryStates.waiting_for_day)
async def history_one_day(message: types.Message, state: FSMContext):
    try:
        d = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except Exception:
        await message.answer("Формат неверный. Пример: 22.07.2025")
        return
    await show_history_result(message, state, d, d)

@router.message(HistoryStates.waiting_for_range)
async def history_range(message: types.Message, state: FSMContext):
    try:
        d1, d2 = message.text.strip().split('-')
        start = datetime.strptime(d1.strip(), "%d.%m.%Y").date()
        end = datetime.strptime(d2.strip(), "%d.%m.%Y").date()
        if end < start:
            start, end = end, start
    except Exception:
        await message.answer("Ошибка формата. Пример: 01.07.2025-31.07.2025")
        return
    await show_history_result(message, state, start, end)

@router.message(HistoryStates.waiting_for_month)
async def history_month(message: types.Message, state: FSMContext):
    try:
        m, y = map(int, message.text.strip().split('.'))
        start = date(y, m, 1)
        end = (date(y, m + 1, 1) - timedelta(days=1)) if m < 12 else date(y, 12, 31)
    except Exception:
        await message.answer("Ошибка формата. Пример: 07.2025")
        return
    await show_history_result(message, state, start, end)

@router.message(HistoryStates.waiting_for_year)
async def history_year(message: types.Message, state: FSMContext):
    try:
        y = int(message.text.strip())
        start = date(y, 1, 1)
        end = date(y, 12, 31)
    except Exception:
        await message.answer("Ошибка формата. Пример: 2025")
        return
    await show_history_result(message, state, start, end)

async def show_history_result(message, state, start: date, end: date):
    user_id = message.from_user.id
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Нет данных по операциям.")
        await state.clear()
        return

    data = await state.get_data()
    scope = data.get("scope")
    period_str = f"{start.strftime('%d.%m.%Y')}" if start == end else f"{start.strftime('%d.%m.%Y')}-{end.strftime('%d.%m.%Y')}"

    if scope == "category":
        category_id = data["category_id"]
        category = await sync_to_async(Category.objects.get)(id=category_id)
        transactions = await sync_to_async(list)(
            Transaction.objects.filter(
                user=user_obj,
                category=category,
                date__gte=start,
                date__lte=end
            ).order_by('date', '-id')
        )
        sign = '+' if category.is_income else '-'
        lines = [f"Операции по категории «{category.name}» за период {period_str}:\n"]
        grouped = {}
        for t in transactions:
            d = t.date
            if d not in grouped:
                grouped[d] = []
            grouped[d].append(f"{sign}{format_rub(float(t.amount))} | {t.description or '-'}")
        for d in sorted(grouped.keys()):
            weekday = WEEKDAYS_RU[d.weekday()]
            lines.append(f"{weekday} {d.strftime('%d.%m.%Y')}:")
            lines.extend(grouped[d])
        total = sum(float(t.amount) for t in transactions)

        label = "Доход" if category.is_income else "Расход"
        lines.append(f"\n{label} по категории: {format_rub(total)}")

        # Проверка лимитов
        limit_msgs = []
        for pt in ("day", "month", "year"):
            limit_str = await check_limit_exceed(user_obj, category, total, pt)
            if limit_str:
                limit_msgs.append(limit_str)
        if limit_msgs:
            lines.extend(limit_msgs)

        # Проверка аномалий
        anomalies = await detect_anomalies(user_obj, start, end)
        if not anomalies:
            anomalies = await detect_anomalies(user_obj, start, end, months_back=2)
        curr_cat_name = category.name
        filtered = [a for a in anomalies if f"«{curr_cat_name}»" in a]
        if filtered:
            lines.append("\n🧐 Аналитика:")
            lines.extend(filtered)
    else:
        transactions = await sync_to_async(list)(
            Transaction.objects.filter(
                user=user_obj, date__gte=start, date__lte=end
            ).select_related('category').order_by('date', '-id')
        )
        grouped = {}
        for t in transactions:
            d = t.date
            if d not in grouped:
                grouped[d] = []
            sign = '+' if t.category.is_income else '-'
            grouped[d].append(
                f"{sign}{format_rub(float(t.amount))} | {t.category.name} | {t.description or '-'}"
            )
        lines = [f"Операции за период {period_str}:\n"]
        for d in sorted(grouped.keys()):
            weekday = WEEKDAYS_RU[d.weekday()]
            lines.append(f"{weekday} {d.strftime('%d.%m.%Y')}:")
            lines.extend(grouped[d])
        sum_income = sum(float(t.amount) for t in transactions if t.category.is_income)
        sum_expense = sum(float(t.amount) for t in transactions if not t.category.is_income)
        balance = sum_income - sum_expense
        lines.append(f"\nДоход: {format_rub(sum_income)}")
        lines.append(f"Расход: {format_rub(sum_expense)}")
        lines.append(f"Баланс: {format_rub(balance)}")

        # Проверка лимитов
        categories = set(t.category for t in transactions)
        limit_blocks = []
        for cat in categories:
            total = sum(float(t.amount) for t in transactions if t.category == cat)
            for pt in ("day", "month", "year"):
                limit_str = await check_limit_exceed(user_obj, cat, total, pt)
                if limit_str:
                    limit_blocks.append(limit_str)
        if limit_blocks:
            lines.extend(limit_blocks)

        # Проверка аномалий
        anomalies = await detect_anomalies(user_obj, start, end)
        if not anomalies:
            anomalies = await detect_anomalies(user_obj, start, end, months_back=2)
        if anomalies:
            lines.append("\n🧐 Аналитика:")
            lines.extend(anomalies)

    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    lines.append(f"Данные предоставлены: {now}")
    await message.answer("\n".join(lines))
    await state.clear()

def register_history_handlers(dp):
    dp.include_router(router)
