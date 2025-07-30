"""
Модуль с эмодзи для Telegram-бота по учёту личных финансов.
Включает: иконки, темы, прогресс-бары, автоподбор, JSON-экспорт.
"""

from typing import Dict, List, Union
from difflib import get_close_matches


# 🎨 ТЕМЫ — разные стили эмодзи в зависимости от темы интерфейса
THEMES = {
    "light": {
        "low_balance": "🧊",
        "overspent": "🔥",
        "goal_reached": "🎉",
        "reminder": "⏰",
    },
    "dark": {
        "low_balance": "🌙",
        "overspent": "💥",
        "goal_reached": "✨",
        "reminder": "🔔",
    }
}


# ─────────────────────────────────────────────────────
# 🔧 ОСНОВНЫЕ ЭМОДЗИ
# ─────────────────────────────────────────────────────
WARNING_EMOJI = "⚠️"
ERROR_EMOJI = "🔴"
SUCCESS_EMOJI = "🟢"
INFO_EMOJI = "ℹ️"
PENDING_EMOJI = "⏳"
OK_EMOJI = "✅"
CANCEL_EMOJI = "❌"
CONFIRM_EMOJI = "✔️"
DENY_EMOJI = "🚫"
HELP_EMOJI = "🆘"
SETTINGS_EMOJI = "⚙️"
BACK_EMOJI = "🔙"
EDIT_EMOJI = "✏️"
DELETE_EMOJI = "🗑️"
ADD_EMOJI = "➕"
REMOVE_EMOJI = "➖"
SEARCH_EMOJI = "🔍"
HISTORY_EMOJI = "📜"
MENU_EMOJI = "📌"
LIST_EMOJI = "📋"
NOTIFICATION_EMOJI = "🔔"
SILENT_EMOJI = "🔕"
COPY_EMOJI = "📋"
LINK_EMOJI = "🔗"
DOWNLOAD_EMOJI = "📥"
UPLOAD_EMOJI = "📤"


# ─────────────────────────────────────────────────────
# 💰 ФИНАНСОВЫЕ ЭМОДЗИ
# ─────────────────────────────────────────────────────
INCOME_EMOJI = "📈"
EXPENSE_EMOJI = "📉"
TRANSFER_EMOJI = "🔄"
SAVINGS_EMOJI = "🏦"
INVESTMENT_EMOJI = "💼"
BALANCE_EMOJI = "⚖️"
BUDGET_EMOJI = "💰"
GOAL_EMOJI = "🎯"
DEBT_EMOJI = "💸"
REFUND_EMOJI = "🔄"
CASH_EMOJI = "💵"
CARD_EMOJI = "💳"
WALLET_EMOJI = "👛"


# ─────────────────────────────────────────────────────
# 📊 ОТЧЁТЫ И СТАТИСТИКА
# ─────────────────────────────────────────────────────
REPORT_EMOJI = "📊"
SUMMARY_EMOJI = "📋"
TODAY_EMOJI = "⏱️"      # Сегодня — "прямо сейчас"
WEEK_EMOJI = "🗓️"       # План на неделю
MONTH_EMOJI = "📅"      # Месяц — календарь
YEAR_EMOJI = "📈"       # Год — тренд, рост
CLOCK_EMOJI = "⏰"       # Время, напоминание


# ─────────────────────────────────────────────────────
# 🛒 КАТЕГОРИИ РАСХОДОВ
# ─────────────────────────────────────────────────────
FOOD_EMOJI = "🍔"
TRANSPORT_EMOJI = "🚗"
ENTERTAINMENT_EMOJI = "🎮"
EDUCATION_EMOJI = "📚"
HEALTH_EMOJI = "🏥"
HOME_EMOJI = "🏠"
CLOTHES_EMOJI = "👕"
GIFTS_EMOJI = "🎁"
UTILITIES_EMOJI = "💡"
PHONE_EMOJI = "📱"
INTERNET_EMOJI = "🌐"
TAXI_EMOJI = "🚕"
COFFEE_EMOJI = "☕"
ALCOHOL_EMOJI = "🍷"
TRAVEL_EMOJI = "✈️"
PETS_EMOJI = "🐾"
CHARITY_EMOJI = "❤️"


# ─────────────────────────────────────────────────────
# 💬 ЭМОЦИИ И ОБРАТНАЯ СВЯЗЬ
# ─────────────────────────────────────────────────────
QUESTION_EMOJI = "❓"
THUMBS_UP_EMOJI = "👍"
THUMBS_DOWN_EMOJI = "👎"
STAR_EMOJI = "⭐"
GEM_EMOJI = "💎"
MONEY_FACE_EMOJI = "🤑"
FIRE_EMOJI = "🔥"
ICE_EMOJI = "🧊"
BULB_EMOJI = "💡"
CLAP_EMOJI = "👏"
PARTY_EMOJI = "🎉"
SAD_EMOJI = "😔"
HAPPY_EMOJI = "😊"


# ─────────────────────────────────────────────────────
# 💵 ВАЛЮТЫ
# ─────────────────────────────────────────────────────
RUB_EMOJI = "🇷🇺"
USD_EMOJI = "🇺🇸"
EUR_EMOJI = "🇪🇺"
GBP_EMOJI = "🇬🇧"

CURRENCY_EMOJIS = {
    "RUB": RUB_EMOJI,
    "USD": USD_EMOJI,
    "EUR": EUR_EMOJI,
    "GBP": GBP_EMOJI,
}


# ─────────────────────────────────────────────────────
# 🎯 ТЕМАТИЧЕСКИЕ НАБОРЫ
# ─────────────────────────────────────────────────────
ACTIONS_SET: List[str] = [ADD_EMOJI, EDIT_EMOJI, DELETE_EMOJI, SEARCH_EMOJI, HISTORY_EMOJI]

FINANCE_OPERATIONS_SET: List[str] = [INCOME_EMOJI, EXPENSE_EMOJI, TRANSFER_EMOJI, REFUND_EMOJI]

STATUS_SET: Dict[str, str] = {
    "success": SUCCESS_EMOJI,
    "error": ERROR_EMOJI,
    "warning": WARNING_EMOJI,
    "info": INFO_EMOJI,
    "pending": PENDING_EMOJI,
}

REPORT_SET: List[str] = [REPORT_EMOJI, SUMMARY_EMOJI, TODAY_EMOJI, WEEK_EMOJI, MONTH_EMOJI, YEAR_EMOJI]

COMMON_CATEGORIES_SET: Dict[str, str] = {
    "Еда": FOOD_EMOJI,
    "Транспорт": TRANSPORT_EMOJI,
    "Кафе": COFFEE_EMOJI,
    "Подписки": "🔁",
    "Коммуналка": UTILITIES_EMOJI,
    "Развлечения": ENTERTAINMENT_EMOJI,
    "Здоровье": HEALTH_EMOJI,
    "Покупки": CLOTHES_EMOJI,
}

REACTIONS_SET: List[str] = [THUMBS_UP_EMOJI, THUMBS_DOWN_EMOJI, STAR_EMOJI, CLAP_EMOJI, PARTY_EMOJI]

MAIN_MENU_ICONS: Dict[str, str] = {
    "income": INCOME_EMOJI,
    "expense": EXPENSE_EMOJI,
    "report": REPORT_EMOJI,
    "budget": BUDGET_EMOJI,
    "settings": SETTINGS_EMOJI,
    "help": HELP_EMOJI,
}


# ─────────────────────────────────────────────────────
# 🌍 ЛОКАЛИЗАЦИЯ КАТЕГОРИЙ (поддержка рус/англ + нечёткий поиск)
# ─────────────────────────────────────────────────────
CATEGORY_ALIASES = {
    # Русские
    "еда": FOOD_EMOJI, "кафе": COFFEE_EMOJI, "кофе": COFFEE_EMOJI,
    "транспорт": TRANSPORT_EMOJI, "машина": TRANSPORT_EMOJI, "поездки": TAXI_EMOJI, "такси": TAXI_EMOJI,
    "развлечения": ENTERTAINMENT_EMOJI, "игры": ENTERTAINMENT_EMOJI, "подписки": "🔁",
    "коммуналка": UTILITIES_EMOJI, "свет": UTILITIES_EMOJI, "вода": UTILITIES_EMOJI, "газ": UTILITIES_EMOJI,
    "здоровье": HEALTH_EMOJI, "лекарства": HEALTH_EMOJI,
    "покупки": CLOTHES_EMOJI, "одежда": CLOTHES_EMOJI,
    "путешествия": TRAVEL_EMOJI, "отпуск": TRAVEL_EMOJI,
    "питомцы": PETS_EMOJI, "благотворительность": CHARITY_EMOJI,
    "доход": INCOME_EMOJI, "расход": EXPENSE_EMOJI, "бюджет": BUDGET_EMOJI,
    "цель": GOAL_EMOJI, "долг": DEBT_EMOJI, "сбережения": SAVINGS_EMOJI,
    "инвестиции": INVESTMENT_EMOJI, "отчет": REPORT_EMOJI, "помощь": HELP_EMOJI,

    # Английские
    "food": FOOD_EMOJI, "coffee": COFFEE_EMOJI,
    "transport": TRANSPORT_EMOJI, "car": TRANSPORT_EMOJI, "rides": TAXI_EMOJI, "taxi": TAXI_EMOJI,
    "entertainment": ENTERTAINMENT_EMOJI, "games": ENTERTAINMENT_EMOJI, "subscriptions": "🔁",
    "utilities": UTILITIES_EMOJI, "electricity": UTILITIES_EMOJI, "water": UTILITIES_EMOJI, "gas": UTILITIES_EMOJI,
    "health": HEALTH_EMOJI, "medicine": HEALTH_EMOJI,
    "shopping": CLOTHES_EMOJI, "clothes": CLOTHES_EMOJI,
    "travel": TRAVEL_EMOJI, "vacation": TRAVEL_EMOJI,
    "pets": PETS_EMOJI, "charity": CHARITY_EMOJI,
    "income": INCOME_EMOJI, "expense": EXPENSE_EMOJI, "budget": BUDGET_EMOJI,
    "goal": GOAL_EMOJI, "debt": DEBT_EMOJI, "savings": SAVINGS_EMOJI,
    "investments": INVESTMENT_EMOJI, "report": REPORT_EMOJI, "help": HELP_EMOJI,
}


def category_emoji(name: str, threshold: float = 0.6) -> str:
    """
    Возвращает эмодзи для категории по названию.
    Использует нечёткое сравнение.
    :param name: Название категории
    :param threshold: Порог схожести (0.0–1.0)
    :return: Эмодзи или "📝"
    """
    if not name or not name.strip():
        return "📝"

    name = name.strip().lower()

    if name in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[name]

    matches = get_close_matches(name, CATEGORY_ALIASES.keys(), n=1, cutoff=threshold)
    return CATEGORY_ALIASES.get(matches[0], "📝") if matches else "📝"


# ─────────────────────────────────────────────────────
# 📊 УНИВЕРСАЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────────────
def status_emoji(status: str) -> str:
    """Возвращает эмодзи по статусу."""
    return STATUS_SET.get(status.lower(), INFO_EMOJI)


def get_notification_icon(alert_type: str, theme: str = "light") -> str:
    """Возвращает иконку уведомления в зависимости от темы."""
    theme_icons = THEMES.get(theme, THEMES["light"])
    return theme_icons.get(alert_type, INFO_EMOJI)


# ─────────────────────────────────────────────────────
# 📊 ЭМОДЗИ-ПРОГРЕСС БАРЫ
# ─────────────────────────────────────────────────────
def progress_bar(percentage: float, width: int = 10) -> str:
    """
    Генерирует текстовый прогресс-бар.
    Пример: 🟡 ▰▰▰▰▰▰▱▱▱▱ 64%
    """
    percent = min(100, max(0, percentage))
    filled = int(width * percent / 100)
    bar = "▰" * filled + "▱" * (width - filled)

    if percent < 50:
        color = "🟢"
    elif percent < 80:
        color = "🟡"
    else:
        color = "🔴"

    return f"{color} {bar} {int(percent)}%"


def budget_progress(used: float, total: float) -> str:
    """Прогресс для бюджета."""
    percentage = (used / total) * 100 if total > 0 else 0
    return progress_bar(percentage)


def goal_progress(current: float, target: float) -> str:
    """Прогресс для финансовой цели."""
    percentage = (current / target) * 100 if target > 0 else 0
    return progress_bar(percentage)


def progress_squares(percentage: float, width: int = 10) -> str:
    """Прогресс в виде квадратов: 🟥 🟨 ▫️"""
    percent = min(100, max(0, percentage))
    filled = int(width * percent / 100)
    squares = ["🟨" if i < filled else "▫️" for i in range(width)]

    if percent < 30:
        color = "🟢"
    elif percent < 70:
        color = "🟡"
    else:
        color = "🔴"

    return f"{color} {' '.join(squares)} {int(percent)}%"


def progress_with_mood(percentage: float) -> str:
    """Прогресс со смайликом-настроением."""
    percent = min(100, max(0, percentage))

    if percent < 50:
        mood = "😊"
    elif percent < 80:
        mood = "😐"
    elif percent < 100:
        mood = "😬"
    else:
        mood = "😱"

    bar = progress_bar(percent, width=8)
    return bar.replace("🟢", mood).replace("🟡", mood).replace("🔴", mood)


# ─────────────────────────────────────────────────────
# 📦 JSON-СОВМЕСТИМЫЙ ЭКСПОРТ (для API / веба)
# ─────────────────────────────────────────────────────
def to_json_serializable() -> Dict[str, Union[str, Dict, List]]:
    """Возвращает данные в формате, пригодном для JSON."""
    return {
        "currencies": CURRENCY_EMOJIS,
        "operations": {
            "income": INCOME_EMOJI,
            "expense": EXPENSE_EMOJI,
            "transfer": TRANSFER_EMOJI,
        },
        "categories": {
            "food": FOOD_EMOJI,
            "transport": TRANSPORT_EMOJI,
            "entertainment": ENTERTAINMENT_EMOJI,
            "utilities": UTILITIES_EMOJI,
            "health": HEALTH_EMOJI,
            "travel": TRAVEL_EMOJI,
        },
        "status": STATUS_SET,
        "themes": THEMES,
        "intervals": {
            "today": TODAY_EMOJI,
            "week": WEEK_EMOJI,
            "month": MONTH_EMOJI,
            "year": YEAR_EMOJI,
        }
    }


# ─────────────────────────────────────────────────────
# 🧩 ЭКСПОРТ ВСЕХ ПУБЛИЧНЫХ СИМВОЛОВ
# ─────────────────────────────────────────────────────
__all__ = [
    # Основные
    "WARNING_EMOJI", "ERROR_EMOJI", "SUCCESS_EMOJI", "INFO_EMOJI", "PENDING_EMOJI",
    "OK_EMOJI", "CANCEL_EMOJI", "CONFIRM_EMOJI", "DENY_EMOJI", "HELP_EMOJI",
    "SETTINGS_EMOJI", "BACK_EMOJI", "EDIT_EMOJI", "DELETE_EMOJI", "ADD_EMOJI",
    "REMOVE_EMOJI", "SEARCH_EMOJI", "HISTORY_EMOJI", "MENU_EMOJI", "LIST_EMOJI",
    "NOTIFICATION_EMOJI", "SILENT_EMOJI", "COPY_EMOJI", "LINK_EMOJI", "DOWNLOAD_EMOJI", "UPLOAD_EMOJI",

    # Финансы
    "INCOME_EMOJI", "EXPENSE_EMOJI", "TRANSFER_EMOJI", "SAVINGS_EMOJI", "INVESTMENT_EMOJI",
    "BALANCE_EMOJI", "BUDGET_EMOJI", "GOAL_EMOJI", "DEBT_EMOJI", "REFUND_EMOJI",
    "CASH_EMOJI", "CARD_EMOJI", "WALLET_EMOJI",

    # Время
    "TODAY_EMOJI", "WEEK_EMOJI", "MONTH_EMOJI", "YEAR_EMOJI", "CLOCK_EMOJI", "REPORT_EMOJI", "SUMMARY_EMOJI",

    # Категории
    "FOOD_EMOJI", "TRANSPORT_EMOJI", "ENTERTAINMENT_EMOJI", "EDUCATION_EMOJI", "HEALTH_EMOJI",
    "HOME_EMOJI", "CLOTHES_EMOJI", "GIFTS_EMOJI", "UTILITIES_EMOJI", "PHONE_EMOJI", "INTERNET_EMOJI",
    "TAXI_EMOJI", "COFFEE_EMOJI", "ALCOHOL_EMOJI", "TRAVEL_EMOJI", "PETS_EMOJI", "CHARITY_EMOJI",

    # Эмоции
    "QUESTION_EMOJI", "THUMBS_UP_EMOJI", "THUMBS_DOWN_EMOJI", "STAR_EMOJI", "GEM_EMOJI",
    "MONEY_FACE_EMOJI", "FIRE_EMOJI", "ICE_EMOJI", "BULB_EMOJI", "CLAP_EMOJI", "PARTY_EMOJI",
    "SAD_EMOJI", "HAPPY_EMOJI",

    # Валюты
    "RUB_EMOJI", "USD_EMOJI", "EUR_EMOJI", "GBP_EMOJI", "CURRENCY_EMOJIS",

    # Наборы
    "ACTIONS_SET", "FINANCE_OPERATIONS_SET", "STATUS_SET", "REPORT_SET",
    "COMMON_CATEGORIES_SET", "REACTIONS_SET", "MAIN_MENU_ICONS",

    # Функции
    "status_emoji", "category_emoji", "get_notification_icon",
    "progress_bar", "budget_progress", "goal_progress",
    "progress_squares", "progress_with_mood", "to_json_serializable",

    # Темы
    "THEMES",
]