from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
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
