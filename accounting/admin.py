from django.contrib import admin
from .models import Company, Category, ClassificationKeyword, Transaction, ProcessingLog

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['company_id', 'company_name', 'created_at', 'updated_at']
    search_fields = ['company_name']
    ordering = ['company_id']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'company', 'category_name', 'category_type', 'created_at']
    list_filter = ['category_type', 'company']
    search_fields = ['category_name', 'company__company_name']
    ordering = ['company', 'category_id']

@admin.register(ClassificationKeyword)
class ClassificationKeywordAdmin(admin.ModelAdmin):
    list_display = ['keyword', 'category', 'created_at']
    list_filter = ['category__company', 'category']
    search_fields = ['keyword', 'category__category_name']
    ordering = ['category', 'keyword']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'transaction_date', 'description', 
        'transaction_type', 'amount', 'company', 'category', 'is_classified'
    ]
    list_filter = [
        'transaction_type', 'is_classified', 'company', 'category',
        'transaction_date'
    ]
    search_fields = ['description', 'company__company_name', 'category__category_name']
    ordering = ['-transaction_date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('transaction_date', 'description', 'branch_name')
        }),
        ('금액 정보', {
            'fields': ('income_amount', 'expense_amount', 'balance_after', 'amount', 'transaction_type')
        }),
        ('분류 정보', {
            'fields': ('company', 'category', 'is_classified')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProcessingLog)
class ProcessingLogAdmin(admin.ModelAdmin):
    list_display = [
        'log_id', 'process_type', 'file_name', 'records_processed',
        'records_successful', 'records_failed', 'created_at'
    ]
    list_filter = ['process_type', 'created_at']
    search_fields = ['file_name', 'error_message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('처리 정보', {
            'fields': ('process_type', 'file_name')
        }),
        ('결과 정보', {
            'fields': ('records_processed', 'records_successful', 'records_failed')
        }),
        ('오류 정보', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
