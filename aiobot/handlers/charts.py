from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from datetime import date, timedelta, datetime
import asyncio
import matplotlib.pyplot as plt
import os, sys, tempfile
from asgiref.sync import sync_to_async
from collections import defaultdict
from aiobot.states import ChartStates

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()
from core.models import Transaction

router = Router()

@router.message(Command("chart"))
async def chart_start(message: types.Message, state: FSMContext):
    await state.set_state(ChartStates.waiting_for_type)
    await message.answer("Построить диаграмму по:\n1. Расходам\n2. Доходам\n\nВведите цифру:")

@router.message(ChartStates.waiting_for_type)
async def chart_type(message: types.Message, state: FSMContext):
    choice = message.text.strip()
    if choice not in ("1", "2"):
        await message.answer("Пожалуйста, введите 1 (расходы) или 2 (доходы).")
        return
    await state.update_data(is_income=(choice == "2"))
    await state.set_state(ChartStates.waiting_for_period)
    await message.answer("Выберите период:\n1. День\n2. Неделя\n3. Месяц\n4. Год\n\nВведите цифру:")

@router.message(ChartStates.waiting_for_period)
async def chart_period(message: types.Message, state: FSMContext):
    periods = {"1": "день", "2": "неделю", "3": "месяц", "4": "год"}
    choice = message.text.strip()
    if choice not in periods:
        await message.answer("Пожалуйста, выберите: 1 (день), 2 (неделя), 3 (месяц), 4 (год).")
        return
    period = periods[choice]
    await state.update_data(period=period)

    data = await state.get_data()
    is_income = data["is_income"]

    user_id = message.from_user.id
    from django.contrib.auth.models import User
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Нет данных по операциям.")
        await state.clear()
        return

    today = date.today()
    if period == "день":
        start = today
        end = today
    elif period == "неделю":
        start = today - timedelta(days=today.weekday())
        end = today
    elif period == "месяц":
        start = date(today.year, today.month, 1)
        end = today
    elif period == "год":
        start = date(today.year, 1, 1)
        end = today

    transactions = await sync_to_async(list)(
        Transaction.objects
            .filter(user=user_obj, category__is_income=is_income, date__gte=start, date__lte=end)
            .select_related('category')
    )
    if not transactions:
        await message.answer("Операций по выбранным условиям не найдено.")
        await state.clear()
        return

    # Группируем суммы по категориям
    by_cat = defaultdict(float)
    for t in transactions:
        by_cat[t.category.name] += float(t.amount)

    # Сортировка по убыванию суммы
    sorted_items = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    labels = [f"{name}" for name, _ in sorted_items]
    sizes = [v for _, v in sorted_items]

    # Строим круговую диаграмму
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.1f%%', startangle=140
    )
    ax.axis('equal')
    diag_title = "Доходы" if is_income else "Расходы"
    plt.title(f"{diag_title} по категориям за {period}")

    # Собираем подпись-легенду для caption в виде "категория: сумма руб."
    caption_lines = []
    for name, v in sorted_items:
        caption_lines.append(f"{name}: {v:.2f} руб.")
    caption = f"{diag_title} по категориям:\n" + "\n".join(caption_lines)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.savefig(tmpfile.name, bbox_inches='tight')
        plt.close()
        file_path = tmpfile.name

    plot_file = FSInputFile(file_path)
    await message.answer_photo(plot_file, caption=caption)
    # Дать системе чуть-чуть времени закрыть файлы (100-200мс)
    await asyncio.sleep(0.1)
    try:
        os.unlink(file_path)
    except PermissionError:
        pass  # иногда Windows всё равно немного держит — игнорируем ошибку
    await state.clear()

def register_chart_handlers(dp):
    dp.include_router(router)
