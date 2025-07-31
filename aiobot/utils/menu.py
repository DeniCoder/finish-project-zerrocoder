"""
aiobot/utils/menu.py

Генерация reply- и inline-клавиатур для Telegram-бота (на базе Aiogram).
Все используемые эмодзи импортируются из aiobot.utils.emojis.
"""

from typing import List, Optional
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiobot.utils.emojis import (
    EXPENSE_EMOJI,
    INCOME_EMOJI,
    HISTORY_EMOJI,
    REPORT_EMOJI,
    FIRE_EMOJI,
    SETTINGS_EMOJI,
    BACK_EMOJI,
    OK_EMOJI,
    CANCEL_EMOJI,
    TODAY_EMOJI,
    MONTH_EMOJI,
    YEAR_EMOJI,
    category_emoji,
)

# ---- REPLY клавиатура главного меню ----

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

# ---- UNIVERSAL INLINE KEYBOARDS ----

def build_limits_main_menu() -> InlineKeyboardMarkup:
    """
    Главное меню для управления лимитами.
    """
    buttons = [
        [InlineKeyboardButton(text=f"{FIRE_EMOJI} Установить лимит", callback_data="set_limit")],
        [InlineKeyboardButton(text=f"{OK_EMOJI} Посмотреть лимиты", callback_data="view_limits")],
        [InlineKeyboardButton(text=f"{CANCEL_EMOJI} Удалить лимит", callback_data="delete_limit")],
        [InlineKeyboardButton(text=f"{BACK_EMOJI} Назад", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def build_type_menu() -> InlineKeyboardMarkup:
    """
    Инлайн-меню выбора типа (расходы или доходы).
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"{EXPENSE_EMOJI} Расходы", callback_data="limit_type_expense"),
            InlineKeyboardButton(text=f"{INCOME_EMOJI} Доходы", callback_data="limit_type_income"),
        ],
        [InlineKeyboardButton(text=f"{BACK_EMOJI} Назад", callback_data="back")]
    ])


def build_period_menu(show_range: bool = False) -> InlineKeyboardMarkup:
    """
    Универсальное меню для выбора периода.
    Опционально может добавить кнопку выбора диапазона.

    :param show_range: Добавлять ли кнопку выбора диапазона (period_range).
    :return: InlineKeyboardMarkup
    """
    row = [
        InlineKeyboardButton(text=f"{TODAY_EMOJI} День", callback_data="period_day"),
        InlineKeyboardButton(text=f"{MONTH_EMOJI} Месяц", callback_data="period_month"),
        InlineKeyboardButton(text=f"{YEAR_EMOJI} Год", callback_data="period_year"),
    ]
    keyboard = [row]
    if show_range:
        keyboard.append([
            InlineKeyboardButton(text=f"{REPORT_EMOJI} Диапазон", callback_data="period_range")
        ])
    keyboard.append([
        InlineKeyboardButton(text=f"{BACK_EMOJI} Назад", callback_data="back")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def build_category_menu(categories: List, prefix: str, back_callback: Optional[str] = None, columns: int = 2) -> InlineKeyboardMarkup:
    """
    Инлайн-меню для выбора категории (расходов или доходов).

    :param categories: List[Category] — список объектов (ожидается поле name и id)
    :param prefix: str — префикс для callback_data (например, 'setlimit_cat')
    :param back_callback: Optional[str] — callback_data для кнопки "Назад", если требуется
    :param columns: int — количество колонок в клавиатуре
    :return: InlineKeyboardMarkup
    """
    keyboard = []
    row = []
    for idx, cat in enumerate(categories, 1):
        text = f"{category_emoji(cat.name)} {cat.name}"
        row.append(InlineKeyboardButton(text=text, callback_data=f"{prefix}_{cat.id}"))
        if idx % columns == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    # Кнопка "Назад"
    if back_callback:
        keyboard.append([InlineKeyboardButton(text=f"{BACK_EMOJI} Назад", callback_data=back_callback)])
    else:
        keyboard.append([InlineKeyboardButton(text=f"{BACK_EMOJI} Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
