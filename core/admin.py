from django.contrib import admin
from .models import Category, Transaction, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_income")
    list_filter = ("is_income",)
    search_fields = ("name",)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "category", "amount", "date")
    list_filter = ("user", "category", "date")
    search_fields = ("description",)

admin.site.register(UserProfile)
