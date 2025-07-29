from aiobot.utils.formatting import format_rub
from asgiref.sync import sync_to_async
from collections import defaultdict
from core.models import Transaction, CategoryLimit
from datetime import date, timedelta

async def check_limit_exceed(user, category, total: float, period_type: str) -> str | None:
    """
    Создает предупреждение о превышении доходов / расходов установленных лимитов по категориям
    на день, месяц, год.
    """
    limit = await sync_to_async(CategoryLimit.objects.filter(
        user=user, category=category, period_type=period_type).first)()
    if limit and total > float(limit.amount):
        exceed_limit = total - float(limit.amount)
        percent = (total - float(limit.amount)) / float(limit.amount) * 100
        return (f"\n🔥 Превышение лимита по категории «{category.name}» "
                f"за {limit.get_period_type_display().lower()}: {format_rub(exceed_limit)} "
                f"(лимит {format_rub(limit.amount)}, превышен на {percent:.1f}%)")
    return None


async def detect_anomalies(
    user, current_start: date, current_end: date, months_back: int = 3
) -> list[str]:
    """
    Создает предупреждение о превышении расходов по категориям, если расходы
    превышают среднее расходы за последние 2-3 месяца.
    """
    # Получаем расходы за текущий месяц
    current_transactions = await sync_to_async(list)(
        Transaction.objects
        .filter(user=user, date__gte=current_start, date__lte=current_end, category__is_income=False)
        .select_related('category')
    )
    current_by_cat = defaultdict(float)
    for t in current_transactions:
        current_by_cat[t.category.name] += float(t.amount)

    # Средние расходы по категориям за последние N месяцев (до текущего)
    anomalies = []
    for cat_name, current_value in current_by_cat.items():
        sum_prev = 0.0
        count_prev = 0
        for delta in range(1, months_back + 1):
            prev_start = (current_start.replace(day=1) - timedelta(days=1)).replace(day=1)
            prev_start = prev_start.replace(month=(current_start.month - delta - 1) % 12 + 1,
                                            year=current_start.year if current_start.month - delta > 0 else current_start.year - 1)
            prev_end = (prev_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            prev_transactions = await sync_to_async(list)(
                Transaction.objects.filter(
                    user=user, category__name=cat_name, category__is_income=False,
                    date__gte=prev_start, date__lte=prev_end
                )
            )
            total = sum(float(t.amount) for t in prev_transactions)
            if total > 0:
                sum_prev += total
                count_prev += 1
        avg_prev = sum_prev / count_prev if count_prev else 0
        if avg_prev > 0 and current_value > avg_prev * 1.10:  # 10% и выше
            percent = (current_value - avg_prev) / avg_prev * 100
            anomalies.append(
                f"⚠️ Обратите внимание: расходы по категории «{cat_name}» "
                f"в этом месяце {format_rub(current_value)} — выше среднего "
                f"чем за прошлые месяцы на {percent:.1f}%."
            )
    return anomalies
