from aiogram import Router, types
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from core.models import FavoriteReport
from django.contrib.auth.models import User
import json

router = Router()

@router.message(Command("favorites"))
async def show_favorites(message: types.Message):
    user_id = message.from_user.id
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
        favorites = await sync_to_async(list)(
            FavoriteReport.objects.filter(user=user_obj).order_by('-created_at')[:10]
        )
        if not favorites:
            await message.answer("У вас нет избранных отчётов.")
            return
        lines = [f"{f.name} ({f.report_type}) — {f.created_at:%d.%m.%Y %H:%M}" for f in favorites]
        await message.answer("Ваши избранные отчёты:\n" + "\n".join(lines))
    except User.DoesNotExist:
        await message.answer("Пользователь не найден.")

@router.message(Command("add_favorite"))
async def add_favorite(message: types.Message):
    user_id = message.from_user.id
    try:
        user_obj = await sync_to_async(User.objects.get)(username=str(user_id))
        # Пример: сохраняем тестовый отчёт
        fav = await sync_to_async(FavoriteReport.objects.create)(
            user=user_obj,
            name="Тестовый отчёт",
            report_type="history",
            params={"type": "history", "period": "month"}
        )
        await message.answer(f"Отчёт '{fav.name}' добавлен в избранное!")
    except User.DoesNotExist:
        await message.answer("Пользователь не найден.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении в избранное: {e}")

def register_favorites_handlers(dp):
    dp.include_router(router)