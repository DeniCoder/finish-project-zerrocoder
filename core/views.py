from rest_framework import viewsets, permissions
from .models import Category, Transaction, Advice, Anomaly, NotificationHistory, UserProfile
from .serializers import CategorySerializer, TransactionSerializer, AdviceSerializer, AnomalySerializer, NotificationHistorySerializer, UserProfileSerializer
from django_filters.rest_framework import DjangoFilterBackend

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
