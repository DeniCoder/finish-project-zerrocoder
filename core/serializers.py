from rest_framework import serializers
from .models import Category, Transaction, Advice, Anomaly, NotificationHistory, UserProfile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'is_income']

class TransactionSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'date', 'description', 'category', 'category_id']
        read_only_fields = ['id', 'user', 'category']

class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['id', 'user', 'category', 'text', 'created_at', 'advice_type']

class AnomalySerializer(serializers.ModelSerializer):
    class Meta:
        model = Anomaly
        fields = ['id', 'user', 'category', 'date', 'description', 'amount']

class NotificationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationHistory
        fields = ['id', 'user', 'notification_type', 'text', 'sent_at', 'status']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'telegram_id']

