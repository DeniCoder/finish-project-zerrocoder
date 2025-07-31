"""
Генерация инлайн- и Reply-клавиатур для Telegram-бота (Aiogram), с эмодзи из emojis.py.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiobot.utils.emojis import (
    EXPENSE_EMOJI, INCOME_EMOJI, HISTORY_EMOJI, REPORT_EMOJI, FIRE_EMOJI,
    SETTINGS_EMOJI, BACK_EMOJI, category_emoji
)
from typing import List, Tuple

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

async def build_category_menu(
    categories: List[Tuple[str, str]],  # [(название категории, callback_data)]
    back_callback: str = None,
    columns: int = 2,
) -> InlineKeyboardMarkup:
    """
    Собирает инлайн-меню выбора категории с эмодзи.
    :param categories: пары (название без эмодзи, callback_data)
    """
    keyboard = []
    row = []
    for idx, (cat_name, code) in enumerate(categories, 1):
        icon = category_emoji(cat_name)
        text = f"{icon} {cat_name}".strip()
        row.append(InlineKeyboardButton(text=text, callback_data=code))
        if idx % columns == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    if back_callback:
        keyboard.append(
            [InlineKeyboardButton(text=f"{BACK_EMOJI} Назад", callback_data=back_callback)]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
