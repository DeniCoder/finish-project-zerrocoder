from aiogram import Router, types
from aiogram.filters import Command
from datetime import datetime
import os, sys
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django

django.setup()
from core.models import Transaction

router = Router()

# Словарь для перевода дней недели
WEEKDAYS_RU = {
    0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'
}

@router.message(Command("history"))
async def show_history(message: types.Message):
    user_id = message.from_user.id

    # Импорт User внутри обработчика, чтобы не было циклических импортов
    from django.contrib.auth.models import User

    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
    except User.DoesNotExist:
        await message.answer("Вы ещё не добавляли ни одной операции.")
        return

    transactions = await sync_to_async(list)(
        Transaction.objects.filter(user=user_obj)
        .select_related('category')
        .order_by('-date', '-id')[:10]
    )

    if not transactions:
        await message.answer("Операций пока нет.")
        return

    # Группируем операции по дате
    grouped = dict()
    for t in transactions:
        d = t.date
        if d not in grouped:
            grouped[d] = []
        sign = '+' if t.category.is_income else '-'
        grouped[d].append(
            f"{sign}{t.amount} | {t.category.name} | {t.description or '-'}"
        )

    # Строим текст ответа с днями недели на русском
    lines = ["Последние 10 операций:"]
    day_keys = sorted(grouped.keys(), reverse=True)

    for d in day_keys:
        weekday = WEEKDAYS_RU[d.weekday()]
        day_head = f"{weekday} {d.strftime('%d.%m.%Y')}:"
        lines.append(day_head)
        for op_str in grouped[d]:
            lines.append(op_str)

    # Время запроса — просто dd.mm.yyyy, HH:MM
    now = datetime.now().strftime("%d.%m.%Y, %H:%M")
    lines.append(f"\nВремя получения информации: {now}")

    await message.answer("\n".join(lines))

def register_history_handlers(dp):
    dp.include_router(router)
