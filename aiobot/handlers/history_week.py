from aiogram import Router, types
from aiogram.filters import Command
from datetime import date, timedelta
import os, sys
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()
from core.models import Transaction

router = Router()

@router.message(Command("week"))
async def show_week(message: types.Message):
    user_id = message.from_user.id
    from django.contrib.auth.models import User
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Вы ещё не добавляли ни одной операции.")
        return

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # понедельник текущей недели

    transactions = await sync_to_async(list)(
        Transaction.objects
        .filter(user=user_obj, date__gte=start_of_week, date__lte=today)
        .select_related('category')
        .order_by('date', '-id')
    )
    if not transactions:
        await message.answer("За эту неделю ещё не было записей.")
        return

    lines = []
    sum_income = 0
    sum_expense = 0
    for t in transactions:
        sign = '+' if t.category.is_income else '-'
        if t.category.is_income:
            sum_income += float(t.amount)
        else:
            sum_expense += float(t.amount)
        lines.append(
            f"{t.date.strftime('%a %d.%m')}: {sign}{t.amount} | {t.category.name} | {t.description or ''}"
        )

    balance = sum_income - sum_expense

    resp_text = (
        f"Операции за текущую неделю:\n" +
        "\n".join(lines) +
        "\n\n"
        f"Доход: {sum_income}\n"
        f"Расход: {sum_expense}\n"
        f"Баланс: {balance}"
    )
    await message.answer(resp_text)

def register_history_week_handlers(dp):
    dp.include_router(router)
