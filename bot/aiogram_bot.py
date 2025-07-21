import os
import sys
from dotenv import load_dotenv
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

# Django инициализация
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()

from core.models import Transaction, Category  # импорт моделей
from .states import AddExpenseStates  # импорт состояний

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

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
        await message.answer("Пожалуйста, введите число. Пример: 250.75")
        return

    # Предложим список категорий расходов
    categories = Category.objects.filter(is_income=False)
    cat_names = "\n".join([f"{cat.id}. {cat.name}" for cat in categories])
    await state.set_state(AddExpenseStates.waiting_for_category)
    await message.answer(f"Выберите категорию (введите номер):\n{cat_names}")

@dp.message(AddExpenseStates.waiting_for_category)
async def add_expense_category(message: types.Message, state: FSMContext):
    try:
        category_id = int(message.text)
        category = Category.objects.get(id=category_id, is_income=False)
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

    # Получаем из state все input'ы пользователя
    try:
        # Сохраняем расход в Django
        user = message.from_user  # Telegram user
        user_id = message.from_user.id

        category = Category.objects.get(id=data["category_id"], is_income=False)

        # Импортируем User из auth, ищем или создаём пользователя
        from django.contrib.auth.models import User
        user_obj, created = User.objects.get_or_create(username=str(user_id), defaults={"first_name": user.first_name or ""})

        Transaction.objects.create(
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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())