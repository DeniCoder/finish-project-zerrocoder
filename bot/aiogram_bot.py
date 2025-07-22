import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

# --- Инициализация Django ORM ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()

from core.models import Transaction, Category
from django.contrib.auth.models import User

# Важно: оборачиваем обращения к ORM!
from asgiref.sync import sync_to_async

# Состояния для FSM диалога (в отдельном файле states.py)
from .states import AddExpenseStates

# --- Загрузка токена из .env ---
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- Команды бота ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я помогу тебе вести учёт расходов и доходов.")

@dp.message(Command("add_expense"))
async def start_add_expense(message: types.Message, state: FSMContext):
    await state.set_state(AddExpenseStates.waiting_for_amount)
    await message.answer("Введите сумму расхода:")

@dp.message(AddExpenseStates.waiting_for_amount)
async def add_expense_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        await state.update_data(amount=amount)
    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 250.75).")
        return

    # Получаем категории расходов асинхронно
    categories = await sync_to_async(list)(Category.objects.filter(is_income=False))
    if not categories:
        await message.answer("Категории расходов ещё не созданы. Добавьте категории через админ-панель Django.")
        await state.clear()
        return

    cat_names = "\n".join([f"{cat.id}. {cat.name}" for cat in categories])
    await state.set_state(AddExpenseStates.waiting_for_category)
    await message.answer(f"Выберите категорию (введите номер):\n{cat_names}")

@dp.message(AddExpenseStates.waiting_for_category)
async def add_expense_category(message: types.Message, state: FSMContext):
    try:
        category_id = int(message.text)
        # Проверяем существование категории
        category = await sync_to_async(Category.objects.get)(id=category_id, is_income=False)
        await state.update_data(category_id=category_id)
    except (ValueError, Category.DoesNotExist):
        await message.answer("Некорректный номер категории. Попробуйте ещё раз.")
        return
    await state.set_state(AddExpenseStates.waiting_for_date)
    await message.answer("Укажите дату расхода в формате ГГГГ-ММ-ДД (или 'сегодня'):")

@dp.message(AddExpenseStates.waiting_for_date)
async def add_expense_date(message: types.Message, state: FSMContext):
    from datetime import datetime, date
    text = message.text.lower().strip()
    if text in ["сегодня", "today"]:
        dt = date.today()
    else:
        try:
            dt = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            await message.answer("Некорректная дата. Пример: 2025-07-21 или 'сегодня'.")
            return
    await state.update_data(date=dt)
    await state.set_state(AddExpenseStates.waiting_for_description)
    await message.answer("Введите описание (или '-' если оставить пустым):")

@dp.message(AddExpenseStates.waiting_for_description)
async def add_expense_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    description = "" if message.text.strip() == "-" else message.text.strip()
    user = message.from_user
    user_id = user.id

    try:
        # Получаем или создаём пользователя Django по его Telegram ID
        user_obj, _ = await sync_to_async(User.objects.get_or_create)(
            username=str(user_id),
            defaults={"first_name": user.first_name or ""}
        )
        category = await sync_to_async(Category.objects.get)(
            id=data["category_id"], is_income=False
        )
        await sync_to_async(Transaction.objects.create)(
            user=user_obj,
            category=category,
            amount=data["amount"],
            date=data["date"],
            description=description
        )
        await message.answer("Расход успешно добавлен!")
    except Exception as e:
        await message.answer(f"Ошибка добавления расхода: {e}")
    finally:
        await state.clear()

# --- Главный запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())