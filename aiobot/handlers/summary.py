from aiogram import Router, types
from aiogram.filters import Command
from datetime import date, datetime
import os, sys
from asgiref.sync import sync_to_async
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()
from core.models import Transaction

router = Router()

@router.message(Command("summary"))
async def show_summary(message: types.Message):
    user_id = message.from_user.id
    from django.contrib.auth.models import User
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Вы ещё не добавляли ни одной операции.")
        return

    today = date.today()
    start_of_month = date(today.year, today.month, 1)

    transactions = await sync_to_async(list)(
        Transaction.objects
            .filter(user=user_obj, date__gte=start_of_month, date__lte=today)
            .select_related('category')
    )
    if not transactions:
        await message.answer("За этот месяц ещё не было данных.")
        return

    sum_income = sum(float(t.amount) for t in transactions if t.category.is_income)
    sum_expense = sum(float(t.amount) for t in transactions if not t.category.is_income)
    balance = sum_income - sum_expense

    from collections import defaultdict
    by_exp_cat = defaultdict(float)
    by_inc_cat = defaultdict(float)
    for t in transactions:
        if t.category.is_income:
            by_inc_cat[t.category.name] += float(t.amount)
        else:
            by_exp_cat[t.category.name] += float(t.amount)

    # Лидер по расходам
    if by_exp_cat:
        biggest_exp_cat = max(by_exp_cat.items(), key=lambda x: x[1])
        cat_exp_name, cat_exp_sum = biggest_exp_cat
        exp_share = cat_exp_sum / sum_expense * 100 if sum_expense else 0
        advice_exp = f"Больше всего расходов за месяц по категории: '{cat_exp_name}' — {cat_exp_sum} руб. ({exp_share:.1f}% всех расходов)."
    else:
        advice_exp = "В этом месяце не было расходов."

    # Лидер по доходам
    if by_inc_cat:
        biggest_inc_cat = max(by_inc_cat.items(), key=lambda x: x[1])
        cat_inc_name, cat_inc_sum = biggest_inc_cat
        inc_share = cat_inc_sum / sum_income * 100 if sum_income else 0
        advice_inc = f"Больше всего доходов за месяц по категории: '{cat_inc_name}' — {cat_inc_sum} руб. ({inc_share:.1f}% всех доходов)."
    else:
        advice_inc = "В этом месяце не было доходов."

    lines = [
        f"Финансовый итог за месяц:",
        f"Доход: {sum_income}",
        f"Расход: {sum_expense}",
        f"Баланс: {balance}",
        "",
        advice_inc,
        advice_exp
    ]
    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    lines.append(f"Время получения информации: {now}")
    await message.answer("\n".join(lines))

def register_summary_handlers(dp):
    dp.include_router(router)
