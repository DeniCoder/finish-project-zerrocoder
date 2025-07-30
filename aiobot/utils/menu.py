"""
Генерация инлайн- и Reply-клавиатур для Telegram-бота (Aiogram), с эмодзи из emojis.py.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiobot.utils.emojis import (
    ADD_EMOJI, EXPENSE_EMOJI, INCOME_EMOJI, HISTORY_EMOJI, REPORT_EMOJI, FIRE_EMOJI,
    MENU_EMOJI, SETTINGS_EMOJI
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=f"{EXPENSE_EMOJI} Добавить расход"),
            KeyboardButton(text=f"{INCOME_EMOJI} Добавить доход"),
        ],
        [KeyboardButton(text=f"{HISTORY_EMOJI} История операций")],
        [
            KeyboardButton(text=f"{REPORT_EMOJI} Статистика"),
            KeyboardButton(text=f"{FIRE_EMOJI} Лимиты"),
        ],
        [KeyboardButton(text=f"{SETTINGS_EMOJI} Настройки")],
    ],
    resize_keyboard=True,
    one_time_keyboard=False,
)

def build_categories_menu(categories: list[str]) -> InlineKeyboardMarkup:
    """Сформировать инлайн-меню для выбора категории — с автоподбором эмодзи."""
    from aiobot.utils.emojis import category_emoji
    buttons = [
        InlineKeyboardButton(
            text=f"{category_emoji(cat)} {cat}",
            callback_data=f"category_{cat}"
        ) for cat in categories
    ]
    menu = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    return menu

def build_period_menu() -> InlineKeyboardMarkup:
    """Сформировать инлайн-меню для выбора периода с эмодзи."""
    from aiobot.utils.emojis import TODAY_EMOJI, WEEK_EMOJI, MONTH_EMOJI, YEAR_EMOJI
    periods = [
        (f"{TODAY_EMOJI} Один день", "period_day"),
        (f"{WEEK_EMOJI} Диапазон", "period_range"),
        (f"{MONTH_EMOJI} Месяц", "period_month"),
        (f"{YEAR_EMOJI} Год", "period_year"),
    ]
    buttons = [InlineKeyboardButton(text=title, callback_data=code) for title, code in periods]
    menu = InlineKeyboardMarkup(inline_keyboard=[[btn] for btn in buttons])
    return menu
