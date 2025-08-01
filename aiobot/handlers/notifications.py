from aiogram import Router, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from core.models import NotificationHistory
from django.contrib.auth.models import User

router = Router()

@router.message(Command("notifications"))
async def show_notifications(message: types.Message):
    user_id = message.from_user.id
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
        notifications = await sync_to_async(list)(
            NotificationHistory.objects.filter(user=user_obj).order_by('-sent_at')[:10]
        )
        if not notifications:
            await message.answer("У вас нет уведомлений.")
            return
        lines = [f"{n.sent_at:%d.%m.%Y %H:%M}: {n.text}" for n in notifications]
        await message.answer("Последние уведомления:\n" + "\n".join(lines))
    except User.DoesNotExist:
        await message.answer("Пользователь не найден.")