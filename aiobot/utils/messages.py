"""
Унификация и шаблоны сообщений для пользователя бота.
"""

from .emojis import (
    OK_EMOJI, CANCEL_EMOJI, HELP_EMOJI, BACK_EMOJI, FIRE_EMOJI, INCOME_EMOJI, EXPENSE_EMOJI,
    REPORT_EMOJI, TODAY_EMOJI
)

MESSAGES = {
    "start": f"{OK_EMOJI} Добро пожаловать в ФинКонтроль! Для работы необходимо зарегистрироваться.",
    "registered": f"{OK_EMOJI} Регистрация успешно завершена. Доступен основной функционал.",
    "need_register": f"{CANCEL_EMOJI} Для доступа к функциям сервиса завершите регистрацию.",
    "add_expense": f"{EXPENSE_EMOJI} Введите сумму расхода:",
    "add_income": f"{INCOME_EMOJI} Введите сумму дохода:",
    "select_category": f"{REPORT_EMOJI} Выберите категорию:",
    "select_date": f"{TODAY_EMOJI} Укажите дату в формате ДД.ММ.ГГГГ (или 'сегодня'):",
    "invalid_number": f"{CANCEL_EMOJI} Пожалуйста, введите корректное число.",
    "operation_cancelled": f"{CANCEL_EMOJI} Операция отменена.",
    "main_menu": "Главное меню:",
    "back_to_menu": f"{BACK_EMOJI} Возврат в главное меню.",
    "limit_exceed": f"{FIRE_EMOJI} Превышение лимита!",
    "ok": f"{OK_EMOJI} Операция выполнена.",
    "fail": f"{CANCEL_EMOJI} Ошибка. Повторите попытку.",
    "not_implemented": f"{HELP_EMOJI} Функция находится в разработке.",
}

def get_message(key: str) -> str:
    """ Вернуть готовое сообщение по ключу. """
    return MESSAGES.get(key, "")