from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, TransactionViewSet, AdviceViewSet, AnomalyViewSet,
    NotificationHistoryViewSet, UserProfileViewSet, FavoriteReportViewSet, HistoryView
)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('transactions', TransactionViewSet)
router.register('advice', AdviceViewSet)
router.register('anomaly', AnomalyViewSet)
router.register('notification_history', NotificationHistoryViewSet)
router.register('user_profile', UserProfileViewSet)
router.register('favorite_reports', FavoriteReportViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]

urlpatterns += [
    path('history/', HistoryView.as_view(), name='history'),
]
