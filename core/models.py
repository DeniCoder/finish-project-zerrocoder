from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import JSONField


class Category(models.Model):
    """
    Категория дохода или расхода.
    SRP: отвечает только за хранение названия категории.
    """
    name = models.CharField(_("Название"), max_length=50)
    is_income = models.BooleanField(
        _("Это доход"), default=False,
        help_text=_("Отметьте, если операции в этой категории считаются доходами.")
    )

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")

    def __str__(self) -> str:
        return self.name


class Transaction(models.Model):
    """
    Финансовая операция.
    Liskov Substitution: любой Transaction заменяем частью кода,
    ожидающей базовый тип models.Model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    amount = models.DecimalField(_("Сумма"), max_digits=10, decimal_places=2)
    date = models.DateField(_("Дата операции"))
    description = models.TextField(_("Описание"), blank=True)

    class Meta:
        verbose_name = _("Операция")
        verbose_name_plural = _("Операции")
        ordering = ["-date"]

    def __str__(self) -> str:
        sign = "+" if self.category.is_income else "-"
        return f"{sign}{self.amount} {self.category.name} ({self.date})"


class CategoryLimit(models.Model):
    PERIOD_CHOICES = [
        ("day", "День"),
        ("month", "Месяц"),
        ("year", "Год"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES, default="month")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'period_type')

    def __str__(self):
        return f"{self.user}: {self.category.name} ({self.get_period_type_display()}) — лимит {self.amount} руб."


class UserProfile(models.Model):
    """
    Профиль пользователя для расширения стандартного User.
    Связывает Telegram ID с User и хранит настройки.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, help_text="Telegram user ID")
    # В будущем можно добавить настройки уведомлений и т.д.

    def __str__(self):
        return f"{self.user.username} (TG: {self.telegram_id})"


class Advice(models.Model):
    """
    Совет для пользователя (например, рекомендация по тратам).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    advice_type = models.CharField(max_length=50, default='general', help_text="Тип совета (например, лимит, аномалия, общие)")

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}... ({self.created_at:%Y-%m-%d})"

class Anomaly(models.Model):
    """
    Аномалия в тратах/доходах пользователя.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}: {self.description[:30]}... ({self.date})"

class NotificationHistory(models.Model):
    """
    История отправленных уведомлений пользователю.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=50, help_text="Тип уведомления (ежедневное, лимит, аномалия и т.д.)")
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent', help_text="Статус уведомления (sent, failed, etc.)")

    def __str__(self):
        return f"{self.user.username}: {self.notification_type} ({self.sent_at:%Y-%m-%d %H:%M})"

class FavoriteReport(models.Model):
    """
    Избранный отчёт пользователя (сохраняет параметры для быстрого доступа).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    report_type = models.CharField(max_length=50, help_text="Тип отчёта: history, chart и т.д.")
    params = JSONField(help_text="Параметры фильтра/отчёта (например, период, категория)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.name} ({self.report_type})"