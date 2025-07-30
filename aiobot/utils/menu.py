"""
Генерация инлайн- и Reply-клавиатур для Telegram-бота (Aiogram).
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить расход"), KeyboardButton(text="Добавить доход")],
        [KeyboardButton(text="История операций")],
        [KeyboardButton(text="Статистика"), KeyboardButton(text="Лимиты")],
        [KeyboardButton(text="Настройки")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)

def build_categories_menu(categories: list[str]) -> InlineKeyboardMarkup:
    """Сформировать инлайн-меню для выбора категории."""
    buttons = [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}") for cat in categories]
    menu = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    return menu

def build_period_menu() -> InlineKeyboardMarkup:
    """Сформировать инлайн-меню для выбора периода."""
    periods = [("Один день", "period_day"), ("Диапазон", "period_range"), ("Месяц", "period_month"), ("Год", "period_year")]
    buttons = [InlineKeyboardButton(text=title, callback_data=code) for title, code in periods]
    menu = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    return menu
