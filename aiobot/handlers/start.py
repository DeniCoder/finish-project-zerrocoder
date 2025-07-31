from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiobot.utils.messages import get_message
from aiobot.utils.menu import main_menu
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start. Проверяет регистрацию пользователя и выводит reply-меню.
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    user_obj, created = await sync_to_async(User.objects.get_or_create)(
        username=str(user_id),
        defaults={"first_name": first_name}
    )
    greeting = get_message("registered") if created else get_message("start")
    await message.answer(
        f"{greeting}\nИспользуйте главное меню для работы:",
        reply_markup=main_menu
    )
    await state.clear()

def register_start_handlers(dp):
    dp.include_router(router)
