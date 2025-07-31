import os
import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# ===== Django setup =====
# Добавляем корень проекта в sys.path, если нужно
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Указываем настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fincontrol.settings")
import django
django.setup()

# ====== Импорт хендлеров (после настройки Django!) ======
from handlers.start import register_start_handlers
from handlers.expenses import register_expense_handlers
from handlers.income import register_income_handlers
from handlers.history import register_history_handlers
from handlers.summary import register_summary_handlers
from handlers.charts import register_chart_handlers
from handlers.limits import register_limit_handlers


# ====== Загрузка переменных окружения ======
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise RuntimeError("API_TOKEN не установлен в .env файле!")

# ====== Настройка логирования ======
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# ====== Создание экземпляров бота и диспетчера ======
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ====== Регистрация всех обработчиков ======
register_expense_handlers(dp)
register_income_handlers(dp)
register_history_handlers(dp)
register_summary_handlers(dp)
register_chart_handlers(dp)
register_limit_handlers(dp)
register_start_handlers(dp)

# ====== Основная точка входа ======
async def main():
    logging.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен вручную.")
    except Exception as exc:
        logging.exception("Ошибка при запуске бота: %s", exc)
