from aiogram import Router, types
from aiogram.filters import Command

import os, sys
from asgiref.sync import sync_to_async

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django

django.setup()
from core.models import Transaction

router = Router()


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

    lines = []
    for t in transactions:
        sign = '+' if t.category.is_income else '-'
        line = f"{sign}{t.amount} | {t.category.name} | {t.date.strftime('%Y-%m-%d')}\n{t.description or ''}"
        lines.append(line)

    resp_text = "Последние 10 операций:\n" + "\n\n".join(lines)
    await message.answer(resp_text)


def register_history_handlers(dp):
    dp.include_router(router)
