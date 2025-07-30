from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.contrib import messages
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
import pandas as pd
from django.utils import timezone
from datetime import datetime

from .models import Company, Category, ClassificationKeyword, Transaction, ProcessingLog
from .serializers import (
    CompanySerializer, CategorySerializer, ClassificationKeywordSerializer,
    TransactionSerializer, ProcessingLogSerializer, SummarySerializer
)
from .forms import TransactionUploadForm

def index(request):
    """홈 페이지"""
    return render(request, 'index.html')

def dashboard(request):
    """대시보드 페이지 (서버 사이드 렌더링)"""
    # 전체 요약
    total_transactions = Transaction.objects.count()
    total_income = Transaction.objects.filter(transaction_type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0
    total_expense = Transaction.objects.filter(transaction_type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # 회사별 요약
    companies_summary = []
    for company in Company.objects.all():
        company_transactions = Transaction.objects.filter(company=company)
        company_income = company_transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        company_expense = company_transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        companies_summary.append({
            'company_name': company.company_name,
            'transaction_count': company_transactions.count(),
            'income': int(company_income),
            'expense': int(company_expense),
            'net': int(company_income - company_expense)
        })
    
    # 계정과목별 요약
    categories_summary = []
    for category in Category.objects.all():
        category_transactions = Transaction.objects.filter(category=category)
        category_income = category_transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        category_expense = category_transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        categories_summary.append({
            'category_name': category.category_name,
            'transaction_count': category_transactions.count(),
            'income': int(category_income),
            'expense': int(category_expense),
            'net': int(category_income - category_expense)
        })
    
    # 거래 내역 (최근 20건)
    transactions = Transaction.objects.select_related('company', 'category').order_by('-transaction_date')[:20]
    
    context = {
        'total_transactions': total_transactions,
        'total_income': int(total_income),
        'total_expense': int(total_expense),
        'net_profit': int(total_income - total_expense),
        'companies_summary': companies_summary,
        'categories_summary': categories_summary,
        'transactions': transactions,
    }
    
    return render(request, 'dashboard.html', context)

def upload_file(request):
    """파일 업로드 처리 (Django Form 사용)"""
    if request.method == 'GET':
        form = TransactionUploadForm()
        return render(request, 'index.html', {'form': form})
    
    if request.method == 'POST':
        form = TransactionUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                
                # 처리 로그 시작
                log = ProcessingLog.objects.create(
                    process_type='import',
                    file_name=file.name,
                    records_processed=0
                )
                
                # CSV 파일 읽기
                df = pd.read_csv(file)
                print(f"[DEBUG] CSV 파일 읽기 완료: {len(df)}행")
                
                success_count = 0
                failed_count = 0
                
                # 기존 거래 내역 삭제 (중복 방지)
                existing_count = Transaction.objects.count()
                print(f"[DEBUG] 기존 거래 내역 삭제 전: {existing_count}건")
                Transaction.objects.all().delete()
                print(f"[DEBUG] 기존 거래 내역 삭제 완료")
                
                for index, row in df.iterrows():
                    try:
                        # 거래 유형 결정
                        if row['입금액'] > 0:
                            transaction_type = 'income'
                            amount = row['입금액']
                        else:
                            transaction_type = 'expense'
                            amount = row['출금액']
                        
                        # 날짜 파싱
                        date_str = row['거래일시']
                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                        aware_date = timezone.make_aware(parsed_date, timezone=timezone.get_current_timezone())
                        
                        # 거래 내역 생성
                        transaction = Transaction.objects.create(
                            transaction_date=aware_date,
                            description=row['적요'],
                            income_amount=row['입금액'],
                            expense_amount=row['출금액'],
                            balance_after=row['거래후잔액'],
                            branch_name=row['거래점'],
                            transaction_type=transaction_type,
                            amount=amount,
                            is_classified=False
                        )
                        success_count += 1
                        
                    except Exception as e:
                        print(f"[DEBUG] 행 {index} 처리 실패: {e}")
                        failed_count += 1
                
                # 로그 업데이트
                log.records_processed = len(df)
                log.records_successful = success_count
                log.records_failed = failed_count
                log.save()
                
                print(f"[DEBUG] CSV 처리 완료: 성공 {success_count}건, 실패 {failed_count}건")
                
                # 자동 분류 실행
                print(f"[DEBUG] 자동 분류 시작")
                classify_transactions()
                
                final_count = Transaction.objects.count()
                print(f"[DEBUG] 최종 거래 건수: {final_count}건")
                
                messages.success(request, f'파일 업로드 완료: 성공 {success_count}건, 실패 {failed_count}건')
                return redirect('dashboard')
                
            except Exception as e:
                messages.error(request, f'파일 업로드 오류: {str(e)}')
                return redirect('upload_file')
        else:
            # 폼 검증 실패
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
            return redirect('upload_file')

def classify_transactions():
    """거래 내역 자동 분류"""
    try:
        # 미분류 거래 조회
        unclassified_transactions = Transaction.objects.filter(is_classified=False)
        print(f"[DEBUG] 분류 시작: 미분류 거래 {unclassified_transactions.count()}건")
        
        # 처리 로그 시작
        log = ProcessingLog.objects.create(
            process_type='classification',
            records_processed=unclassified_transactions.count()
        )
        
        success_count = 0
        failed_count = 0
        
        for transaction in unclassified_transactions:
            try:
                # 키워드 매칭으로 분류
                keywords = ClassificationKeyword.objects.select_related('category', 'category__company')
                
                for keyword_obj in keywords:
                    print(f"[DEBUG] 키워드 매칭 시도: '{keyword_obj.keyword}' in '{transaction.description}'")
                    if keyword_obj.keyword in transaction.description:
                        print(f"[DEBUG] 매칭 성공: {keyword_obj.keyword} -> {keyword_obj.category.company.company_name} - {keyword_obj.category.category_name}")
                        # 업데이트만 수행 (새 레코드 생성 방지)
                        Transaction.objects.filter(transaction_id=transaction.transaction_id).update(
                            company=keyword_obj.category.company,
                            category=keyword_obj.category,
                            is_classified=True
                        )
                        success_count += 1
                        break
                else:
                    print(f"[DEBUG] 매칭 실패: '{transaction.description}' - 키워드 없음")
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
        
        # 로그 업데이트
        log.records_successful = success_count
        log.records_failed = failed_count
        log.save()
        
        print(f"[DEBUG] 분류 완료: 성공 {success_count}건, 실패 {failed_count}건")
        print(f"[DEBUG] 분류 후 총 거래 건수: {Transaction.objects.count()}건")
        
    except Exception as e:
        print(f"[DEBUG] 분류 오류: {e}")

@api_view(['GET'])
def api_summary(request):
    """요약 정보 API"""
    try:
        # 전체 요약
        total_transactions = Transaction.objects.count()
        total_income = Transaction.objects.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        total_expense = Transaction.objects.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # 회사별 요약
        companies_summary = []
        for company in Company.objects.all():
            company_transactions = Transaction.objects.filter(company=company)
            company_income = company_transactions.filter(transaction_type='income').aggregate(
                total=Sum('amount')
            )['total'] or 0
            company_expense = company_transactions.filter(transaction_type='expense').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            companies_summary.append({
                'company_name': company.company_name,
                'transaction_count': company_transactions.count(),
                'income': int(company_income),
                'expense': int(company_expense),
                'net': int(company_income - company_expense)
            })
        
        # 계정과목별 요약
        categories_summary = []
        for category in Category.objects.all():
            category_transactions = Transaction.objects.filter(category=category)
            category_income = category_transactions.filter(transaction_type='income').aggregate(
                total=Sum('amount')
            )['total'] or 0
            category_expense = category_transactions.filter(transaction_type='expense').aggregate(
                total=Sum('amount')
            )['total'] or 0
            
            categories_summary.append({
                'category_name': category.category_name,
                'transaction_count': category_transactions.count(),
                'income': int(category_income),
                'expense': int(category_expense),
                'net': int(category_income - category_expense)
            })
        
        summary_data = {
            'total_transactions': total_transactions,
            'total_income': int(total_income),
            'total_expense': int(total_expense),
            'companies': companies_summary,
            'categories': categories_summary
        }
        
        return Response({
            'success': True,
            'data': summary_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'요약 정보 조회 오류: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def api_process_accounting(request):
    """회계 처리 API"""
    try:
        data = request.data
        
        if 'csv_data' in data:
            # CSV 데이터를 임시 파일로 저장
            df = pd.DataFrame(data['csv_data'])
            
            # 처리 로그 시작
            log = ProcessingLog.objects.create(
                process_type='api_import',
                file_name='api_data.csv',
                records_processed=len(df)
            )
            
            success_count = 0
            failed_count = 0
            
            for _, row in df.iterrows():
                try:
                    # 거래 유형 결정
                    if row['입금액'] > 0:
                        transaction_type = 'income'
                        amount = row['입금액']
                    else:
                        transaction_type = 'expense'
                        amount = row['출금액']
                    
                    # 날짜 파싱
                    date_str = row['거래일시']
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    aware_date = timezone.make_aware(parsed_date, timezone=timezone.get_current_timezone())
                    
                    # 거래 내역 생성
                    transaction = Transaction.objects.create(
                        transaction_date=aware_date,
                        description=row['적요'],
                        income_amount=row['입금액'],
                        expense_amount=row['출금액'],
                        balance_after=row['거래후잔액'],
                        branch_name=row['거래점'],
                        transaction_type=transaction_type,
                        amount=amount,
                        is_classified=False
                    )
                    success_count += 1
                    
                except Exception as e:
                    failed_count += 1
            
            # 로그 업데이트
            log.records_successful = success_count
            log.records_failed = failed_count
            log.save()
            
            # 자동 분류 실행
            classify_transactions()
            
            return Response({
                'success': True,
                'message': f'회계 처리 완료: 성공 {success_count}건, 실패 {failed_count}건'
            })
        
        return Response({
            'success': False,
            'message': 'CSV 데이터가 제공되지 않았습니다.'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'회계 처리 오류: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ViewSets
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    
    def get_serializer_class(self):
        return CompanySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    @action(detail=False, methods=['get'])
    def unclassified(self, request):
        """미분류 거래 조회"""
        unclassified = Transaction.objects.filter(is_classified=False)
        serializer = self.get_serializer(unclassified, many=True)
        return Response(serializer.data)

class ProcessingLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProcessingLog.objects.all()
    serializer_class = ProcessingLogSerializer
