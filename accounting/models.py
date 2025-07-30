from django.db import models
from django.utils import timezone

class Company(models.Model):
    """회사 정보 모델"""
    company_id = models.CharField(max_length=20, primary_key=True)
    company_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'companies'
        verbose_name = '회사'
        verbose_name_plural = '회사들'

    def __str__(self):
        return self.company_name

class Category(models.Model):
    """계정과목 모델"""
    CATEGORY_TYPES = [
        ('income', '수익'),
        ('expense', '비용'),
        ('neutral', '중립'),
    ]
    
    category_id = models.CharField(max_length=20, primary_key=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='categories')
    category_name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = '계정과목'
        verbose_name_plural = '계정과목들'

    def __str__(self):
        return f"{self.company.company_name} - {self.category_name}"

class ClassificationKeyword(models.Model):
    """분류 키워드 모델"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classification_keywords'
        verbose_name = '분류 키워드'
        verbose_name_plural = '분류 키워드들'
        unique_together = ['keyword', 'category']

    def __str__(self):
        return f"{self.category.category_name} - {self.keyword}"

class Transaction(models.Model):
    """거래 내역 모델"""
    TRANSACTION_TYPES = [
        ('income', '입금'),
        ('expense', '출금'),
    ]
    
    transaction_id = models.AutoField(primary_key=True)
    transaction_date = models.DateTimeField()
    description = models.CharField(max_length=200)
    income_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    expense_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    branch_name = models.CharField(max_length=100, blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_classified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transactions'
        verbose_name = '거래 내역'
        verbose_name_plural = '거래 내역들'
        indexes = [
            models.Index(fields=['transaction_date']),
            models.Index(fields=['company']),
            models.Index(fields=['category']),
            models.Index(fields=['is_classified']),
        ]

    def __str__(self):
        return f"{self.transaction_date.strftime('%Y-%m-%d')} - {self.description}"

class ProcessingLog(models.Model):
    """처리 로그 모델"""
    PROCESS_TYPES = [
        ('import', '가져오기'),
        ('classification', '분류'),
        ('export', '내보내기'),
    ]
    
    log_id = models.AutoField(primary_key=True)
    process_type = models.CharField(max_length=20, choices=PROCESS_TYPES)
    file_name = models.CharField(max_length=200, blank=True, null=True)
    records_processed = models.IntegerField(default=0)
    records_successful = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processing_logs'
        verbose_name = '처리 로그'
        verbose_name_plural = '처리 로그들'

    def __str__(self):
        return f"{self.process_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
