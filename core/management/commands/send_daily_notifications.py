from django.core.management.base import BaseCommand
from core.models import UserProfile, NotificationHistory
from django.contrib.auth.models import User
from datetime import datetime

class Command(BaseCommand):
    help = 'Отправляет ежедневные уведомления пользователям с Telegram ID.'

    def handle(self, *args, **kwargs):
        profiles = UserProfile.objects.exclude(telegram_id__isnull=True)
        for profile in profiles:
            user = profile.user
            text = f'Ваш ежедневный отчёт на {datetime.now().strftime("%d.%m.%Y")}'
            NotificationHistory.objects.create(
                user=user,
                notification_type='daily',
                text=text,
                status='sent'
            )
            self.stdout.write(self.style.SUCCESS(f'Уведомление для {user.username} ({profile.telegram_id}) создано.'))