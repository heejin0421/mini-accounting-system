from rest_framework import serializers
from .models import Company, Category, ClassificationKeyword, Transaction, ProcessingLog

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class ClassificationKeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationKeyword
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    keywords = ClassificationKeywordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'

class CompanyDetailSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Company
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    
    # 금액 필드들을 정수로 변환
    income_amount = serializers.SerializerMethodField()
    expense_amount = serializers.SerializerMethodField()
    balance_after = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    
    def get_income_amount(self, obj):
        return int(obj.income_amount) if obj.income_amount else 0
    
    def get_expense_amount(self, obj):
        return int(obj.expense_amount) if obj.expense_amount else 0
    
    def get_balance_after(self, obj):
        return int(obj.balance_after) if obj.balance_after else 0
    
    def get_amount(self, obj):
        return int(obj.amount) if obj.amount else 0
    
    class Meta:
        model = Transaction
        fields = '__all__'

class ProcessingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingLog
        fields = '__all__'

class SummarySerializer(serializers.Serializer):
    total_transactions = serializers.IntegerField()
    total_income = serializers.IntegerField()
    total_expense = serializers.IntegerField()
    companies = serializers.ListField()
    categories = serializers.ListField() 