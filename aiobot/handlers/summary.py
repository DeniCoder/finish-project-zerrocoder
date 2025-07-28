from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from datetime import date, datetime, timedelta
import os, tempfile, asyncio
from asgiref.sync import sync_to_async
import matplotlib.pyplot as plt
from collections import defaultdict
from aiobot.states import SummaryStates
from aiobot.utils.formatting import format_rub
from aiobot.utils.anomalies import detect_anomalies


router = Router()

@router.message(F.text.casefold() == "отмена")
async def cancel_fsm(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод отменён.")

def format_period(start: date, end: date) -> str:
    if start == end:
        return start.strftime("%d.%m.%Y")
    return f"{start.strftime('%d.%m.%Y')}-{end.strftime('%d.%m.%Y')}"

@router.message(Command("summary"))
async def summary_start(message: types.Message, state: FSMContext):
    await state.set_state(SummaryStates.waiting_for_period_type)
    await message.answer(
        "За какой период вывести итог?\n"
        "1. Один день\n"
        "2. Диапазон дат\n"
        "3. Месяц\n"
        "4. Год\n\nУкажите цифру:"
    )

@router.message(SummaryStates.waiting_for_period_type)
async def summary_period_choose(message: types.Message, state: FSMContext):
    periods = {"1": "day", "2": "range", "3": "month", "4": "year"}
    choice = message.text.strip()
    if choice not in periods:
        await message.answer("Пожалуйста, выберите: 1 (день), 2 (диапазон дат), 3 (месяц), 4 (год).")
        return
    period_type = periods[choice]
    await state.update_data(period_type=period_type)
    if period_type == "day":
        await state.set_state(SummaryStates.waiting_for_day)
        await message.answer("Введите дату в формате ДД.ММ.ГГГГ (например, 22.07.2025):")
    elif period_type == "range":
        await state.set_state(SummaryStates.waiting_for_range)
        await message.answer("Введите диапазон: ДД.ММ.ГГГГ-ДД.ММ.ГГГГ (напр., 01.07.2025-15.07.2025):")
    elif period_type == "month":
        await state.set_state(SummaryStates.waiting_for_month)
        await message.answer("Введите месяц и год: ММ.ГГГГ (например, 07.2025):")
    elif period_type == "year":
        await state.set_state(SummaryStates.waiting_for_year)
        await message.answer("Введите год (например, 2025):")

@router.message(SummaryStates.waiting_for_day)
async def summary_one_day(message: types.Message, state: FSMContext):
    try:
        d = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except Exception:
        await message.answer("Ошибка формата. Пример: 22.07.2025")
        return
    await prepare_and_send_summary(message, state, d, d)

@router.message(SummaryStates.waiting_for_range)
async def summary_range(message: types.Message, state: FSMContext):
    try:
        d1, d2 = message.text.strip().split('-')
        start = datetime.strptime(d1.strip(), "%d.%m.%Y").date()
        end = datetime.strptime(d2.strip(), "%d.%m.%Y").date()
        if end < start:
            start, end = end, start
    except Exception:
        await message.answer("Ошибка формата. Пример: 01.07.2025-31.07.2025")
        return
    await prepare_and_send_summary(message, state, start, end)

@router.message(SummaryStates.waiting_for_month)
async def summary_month(message: types.Message, state: FSMContext):
    try:
        m, y = map(int, message.text.strip().split('.'))
        start = date(y, m, 1)
        if m == 12:
            end = date(y, 12, 31)
        else:
            end = date(y, m + 1, 1) - timedelta(days=1)
    except Exception:
        await message.answer("Ошибка формата. Пример: 07.2025")
        return
    await prepare_and_send_summary(message, state, start, end)

@router.message(SummaryStates.waiting_for_year)
async def summary_year(message: types.Message, state: FSMContext):
    try:
        y = int(message.text.strip())
        start = date(y, 1, 1)
        end = date(y, 12, 31)
    except Exception:
        await message.answer("Ошибка формата. Пример: 2025")
        return
    await prepare_and_send_summary(message, state, start, end)

async def prepare_and_send_summary(message, state, start: date, end: date):
    from core.models import Transaction
    from django.contrib.auth.models import User

    user_id = message.from_user.id
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Нет данных по операциям.")
        await state.clear()
        return

    transactions = await sync_to_async(list)(
        Transaction.objects
            .filter(user=user_obj, date__gte=start, date__lte=end)
            .select_related('category')
    )
    if not transactions:
        await message.answer("В указанный период операций не найдено.")
        await state.clear()
        return

    income_by_cat = defaultdict(float)
    expense_by_cat = defaultdict(float)
    sum_income = 0
    sum_expense = 0
    for t in transactions:
        if t.category.is_income:
            income_by_cat[t.category.name] += float(t.amount)
            sum_income += float(t.amount)
        else:
            expense_by_cat[t.category.name] += float(t.amount)
            sum_expense += float(t.amount)
    balance = sum_income - sum_expense

    # --- График
    groups = []
    income_labels = []
    income_vals = []
    for k, v in sorted(income_by_cat.items(), key=lambda x: x[1], reverse=True):
        income_labels.append(f"{k} ({v/sum_income*100:.1f}%)" if sum_income else k)
        income_vals.append(v)
    if sum_income:
        groups.append(('Доход', income_labels, income_vals))

    expense_labels = []
    expense_vals = []
    for k, v in sorted(expense_by_cat.items(), key=lambda x: x[1], reverse=True):
        expense_labels.append(f"{k} ({v/sum_expense*100:.1f}%)" if sum_expense else k)
        expense_vals.append(v)
    if sum_expense:
        groups.append(('Расход', expense_labels, expense_vals))

    # Стандартные cmap палитры для разных групп
    cmap = plt.get_cmap('tab20')
    colors_income = [cmap(i) for i in range(10)]  # уникальные цвета для доходов
    colors_expense = [cmap(i) for i in range(10, 20)]  # другие уникальные цвета для расходов

    fig, ax = plt.subplots(figsize=(7, 5))
    bar_width = 0.3

    for i, (label, sublabels, vals) in enumerate(groups):
        bottom = 0
        colors = colors_income if label == 'Доход' else colors_expense
        for idx, (v, cat_label) in enumerate(zip(vals, sublabels)):
            ax.bar(
                i, v, bar_width, bottom=bottom, label=cat_label,
                color=colors[idx % len(colors)],
            )
            bottom += v


    ax.set_xlim(-0.3, 1.3)

    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([label for label, _, _ in groups])
    ax.set_ylabel("Сумма, руб.")
    period_str = format_period(start, end)
    plt.title(f"Доходы и расходы за период {period_str}")

    # Подписи категорий со всеми метками и цветами
    handles, labels_ = ax.get_legend_handles_labels()
    # Уникальные лейблы только один раз
    seen = set()
    custom = []
    for h, l in zip(handles, labels_):
        if l not in seen:
            custom.append((h, l))
            seen.add(l)
    ax.legend([h for h, _ in custom], [l for _, l in custom], loc="upper right")

    # Сохраняем картинку и отправляем пользователю
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        plt.tight_layout()
        plt.savefig(tmpfile.name, bbox_inches='tight')
        plt.close()
        plot_file = FSInputFile(tmpfile.name)
        file_path = tmpfile.name

    # Определяем крупнейшие категории и их долю
    if income_by_cat:
        big_income_cat, big_income_val = max(income_by_cat.items(), key=lambda x: x[1])
        income_share = big_income_val / sum_income * 100 if sum_income else 0
        inc_text = f"Больше всего доходов по категории: \n{big_income_cat} — {format_rub(big_income_val)} ({income_share:.1f}% всех доходов)."
    else:
        inc_text = "В выбранном периоде не было доходов."
    if expense_by_cat:
        big_exp_cat, big_exp_val = max(expense_by_cat.items(), key=lambda x: x[1])
        exp_share = big_exp_val / sum_expense * 100 if sum_expense else 0
        exp_text = f"Больше всего расходов по категории: \n{big_exp_cat} — {format_rub(big_exp_val)} ({exp_share:.1f}% всех расходов)."
    else:
        exp_text = "В выбранном периоде не было расходов."

    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    anomalies = await detect_anomalies(user_obj, start, end, months_back=3)

    caption_lines = [
        f"Финансовый итог: {format_rub(balance)}",
        f"Доход: {format_rub(sum_income)}",
        f"Расход: {format_rub(sum_expense)}",
        "",
        inc_text,
        exp_text,
    ]

    # Вставляем советы, если есть аномалии
    if anomalies:
        caption_lines.append("\n🧐 Аналитика:")
        caption_lines.extend(anomalies)

    caption_lines.append(f"Данные предоставлены: {now}")
    caption = "\n".join(caption_lines)

    await message.answer_photo(plot_file, caption=caption)
    await asyncio.sleep(0.2)
    try:
        os.unlink(file_path)
    except PermissionError:
        pass

    await state.clear()

def register_summary_handlers(dp):
    dp.include_router(router)
