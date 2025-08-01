from rest_framework import viewsets, permissions
from .models import Category, Transaction, Advice, Anomaly, NotificationHistory, UserProfile, FavoriteReport
from .serializers import CategorySerializer, TransactionSerializer, AdviceSerializer, AnomalySerializer, NotificationHistorySerializer, UserProfileSerializer, FavoriteReportSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction, Category
from django.utils import timezone
from datetime import datetime

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_income']

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    queryset = Transaction.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'category', 'date']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AdviceViewSet(viewsets.ModelViewSet):
    queryset = Advice.objects.all()
    serializer_class = AdviceSerializer

class AnomalyViewSet(viewsets.ModelViewSet):
    queryset = Anomaly.objects.all()
    serializer_class = AnomalySerializer

class NotificationHistoryViewSet(viewsets.ModelViewSet):
    queryset = NotificationHistory.objects.all()
    serializer_class = NotificationHistorySerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class FavoriteReportViewSet(viewsets.ModelViewSet):
    queryset = FavoriteReport.objects.all()
    serializer_class = FavoriteReportSerializer

class HistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'core/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        qs = Transaction.objects.filter(user=user)
        # Фильтры
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        category_id = self.request.GET.get('category')
        if date_from:
            try:
                dt_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                qs = qs.filter(date__gte=dt_from)
            except Exception:
                pass
        if date_to:
            try:
                dt_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                qs = qs.filter(date__lte=dt_to)
            except Exception:
                pass
        if category_id:
            try:
                qs = qs.filter(category_id=int(category_id))
            except Exception:
                pass
        qs = qs.select_related('category').order_by('-date', '-id')
        context['transactions'] = qs
        context['categories'] = Category.objects.all()
        context['date_from'] = date_from or ''
        context['date_to'] = date_to or ''
        context['category_id'] = int(category_id) if category_id else ''
        return context
