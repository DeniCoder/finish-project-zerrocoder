"""
Строит круговую диаграмму или расходов, или доходов за произвольный период,
добавляет в caption предупреждения о превышении лимита и аномальных тратах.
"""

import django
import matplotlib.pyplot as plt
import os, sys, tempfile, asyncio
from aiobot.states import ChartStates
from aiobot.utils.anomalies import check_limit_exceed, detect_anomalies
from aiobot.utils.formatting import format_rub
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from asgiref.sync import sync_to_async
from collections import defaultdict
from core.models import Transaction, Category
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")

django.setup()

router = Router()

@router.message(F.text.casefold() == "отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод отменён.")

@router.message(Command("chart"))
async def chart_start(message: types.Message, state: FSMContext):
    await state.set_state(ChartStates.waiting_for_type)
    await message.answer("Построить диаграмму по:\n1. Расходам\n2. Доходам\n\n"
                         "Введите цифру (1 или 2):")

@router.message(ChartStates.waiting_for_type)
async def chart_type(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    if choice not in ("1", "2"):
        await message.answer("Пожалуйста, введите 1 (расходы) или 2 (доходы).")
        return
    await state.update_data(is_income=(choice == "2"))
    await state.set_state(ChartStates.waiting_for_period_type)
    await message.answer(
        "Выберите тип периода:\n"
        "1. Один день\n"
        "2. Диапазон дат\n"
        "3. Месяц\n"
        "4. Год\n\nВведите цифру:"
    )

@router.message(ChartStates.waiting_for_period_type)
async def chart_period_select(message: types.Message, state: FSMContext):
    periods = {"1": "day", "2": "range", "3": "month", "4": "year"}
    choice = message.text.strip()
    if choice not in periods:
        await message.answer("Пожалуйста, выберите: 1 (один день), 2 (диапазон дат), 3 (месяц), 4 (год).")
        return
    period_type = periods[choice]
    await state.update_data(period_type=period_type)
    if period_type == "day":
        await state.set_state(ChartStates.waiting_for_day)
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ (например, 22.07.2025):")
    elif period_type == "range":
        await state.set_state(ChartStates.waiting_for_range)
        await message.answer("Введите диапазон через дефис: ДД.ММ.ГГГГ-ДД.ММ.ГГГГ (например, 01.07.2025-15.07.2025):")
    elif period_type == "month":
        await state.set_state(ChartStates.waiting_for_month)
        await message.answer("Введите месяц и год в формате ММ.ГГГГ (например, 07.2025):")
    elif period_type == "year":
        await state.set_state(ChartStates.waiting_for_year)
        await message.answer("Введите год в формате ГГГГ (например, 2025):")

@router.message(ChartStates.waiting_for_day)
async def period_day(message: types.Message, state: FSMContext):
    try:
        chosen_day = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Некорректная дата. Пример: 22.07.2025")
        return
    await draw_chart(message, state, start=chosen_day, end=chosen_day)

@router.message(ChartStates.waiting_for_range)
async def period_range(message: types.Message, state: FSMContext):
    try:
        d1, d2 = message.text.strip().split('-')
        start = datetime.strptime(d1.strip(), "%d.%m.%Y").date()
        end = datetime.strptime(d2.strip(), "%d.%m.%Y").date()
        if end < start:
            start, end = end, start
    except Exception:
        await message.answer("Некорректный формат диапазона. Пример: 01.07.2025-31.07.2025")
        return
    await draw_chart(message, state, start=start, end=end)

@router.message(ChartStates.waiting_for_month)
async def period_month(message: types.Message, state: FSMContext):
    try:
        m_str = message.text.strip()
        month, year = map(int, m_str.split('.'))
        start = date(year, month, 1)
        if month == 12:
            end = date(year, 12, 31)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
    except Exception:
        await message.answer("Ошибка формата. Пример: 07.2025")
        return
    await draw_chart(message, state, start=start, end=end)

@router.message(ChartStates.waiting_for_year)
async def period_year(message: types.Message, state: FSMContext):
    try:
        year = int(message.text.strip())
        start = date(year, 1, 1)
        end = date(year, 12, 31)
    except ValueError:
        await message.answer("Ошибка формата. Пример: 2025")
        return
    await draw_chart(message, state, start=start, end=end)

async def draw_chart(message: types.Message, state: FSMContext, start: date, end: date):
    data = await state.get_data()
    is_income = data["is_income"]
    user_id = message.from_user.id

    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Нет данных по операциям.")
        await state.clear()
        return

    transactions = await sync_to_async(list)(
        Transaction.objects
            .filter(user=user_obj, category__is_income=is_income, date__gte=start, date__lte=end)
            .select_related('category')
    )
    if not transactions:
        await message.answer("Операций по выбранным условиям не найдено.")
        await state.clear()
        return

    by_cat = defaultdict(float)
    for t in transactions:
        by_cat[t.category.name] += float(t.amount)
    sorted_items = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    labels = [name for name, _ in sorted_items]
    sizes = [v for _, v in sorted_items]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=140
    )
    ax.axis('equal')
    diag_title = "Доходы" if is_income else "Расходы"
    if start == end:
        title_str = f"{diag_title} по категориям за {start.strftime('%d.%m.%Y')}"
    else:
        title_str = f"{diag_title} по категориям за период {start.strftime('%d.%m.%Y')}-{end.strftime('%d.%m.%Y')}"
    plt.title(title_str)

    sum_amount = sum(by_cat.values())

    # Проверка на превышение лимита
    limit_msgs = []
    for name, v in sorted_items:
        # Поиск объекта категории:
        cat_obj = await sync_to_async(Category.objects.get)(name=name, is_income=is_income)
        for pt in ("day", "month", "year"):
            limit_str = await check_limit_exceed(user_obj, cat_obj, v, pt)
            if limit_str:
                limit_msgs.append(limit_str)

    # Проверка на наличие аномалий
    anomaly_msgs = []
    anomalies = await detect_anomalies(user_obj, start, end)
    if not anomalies:
        anomalies = await detect_anomalies(user_obj, start, end, months_back=2)
    if anomalies:
        anomaly_msgs.append("\n🧐 Аналитика:")
        anomaly_msgs.extend(anomalies)

    # Собираем подпись к картинке с аналитикой
    caption_lines = [f"{diag_title} всего: {format_rub(sum_amount)}"]
    caption_lines.extend(f"{name}: {format_rub(v)}" for name, v in sorted_items)
    if limit_msgs:
        caption_lines.extend(limit_msgs)
    if anomaly_msgs:
        caption_lines.extend(anomaly_msgs)

    # Добавляем дату предоставления данных
    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    caption_lines.append(f"Время получения информации: {now}")

    caption = "\n".join(caption_lines)

    # Сохраняем картинку для отправки пользователю
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.tight_layout()
        plt.savefig(tmpfile.name, bbox_inches='tight')
        plt.close()
        file_path = tmpfile.name
        plot_file = FSInputFile(file_path)

    # Отправляем картинку с подписью
    await message.answer_photo(plot_file, caption=caption)
    await asyncio.sleep(0.2)
    try:
        os.unlink(file_path)
    except PermissionError:
        pass
    await state.clear()

def register_chart_handlers(dp):
    dp.include_router(router)
