from django.core.management.base import BaseCommand
from accounting.models import Company, Category, ClassificationKeyword

class Command(BaseCommand):
    help = '초기 회사 및 분류 규칙 데이터를 생성합니다.'

    def handle(self, *args, **options):
        self.stdout.write('초기 데이터를 생성합니다...')
        
        # 회사 생성
        company_a, created = Company.objects.get_or_create(
            company_id='com_1',
            defaults={'company_name': 'A 커머스'}
        )
        if created:
            self.stdout.write(f'✓ 회사 생성: {company_a.company_name}')
        
        company_b, created = Company.objects.get_or_create(
            company_id='com_2',
            defaults={'company_name': 'B 커머스'}
        )
        if created:
            self.stdout.write(f'✓ 회사 생성: {company_b.company_name}')
        
        # A 커머스 계정과목 및 키워드
        categories_a = [
            ('cat_101', '매출', 'income', ['네이버페이', '쿠팡']),
            ('cat_102', '식비', 'expense', ['배달의민족', '김밥천국']),
            ('cat_103', '사무용품비', 'expense', ['오피스디포']),
        ]
        
        for cat_id, cat_name, cat_type, keywords in categories_a:
            category, created = Category.objects.get_or_create(
                category_id=cat_id,
                defaults={
                    'company': company_a,
                    'category_name': cat_name,
                    'category_type': cat_type
                }
            )
            if created:
                self.stdout.write(f'✓ 계정과목 생성: {category.category_name}')
            
            for keyword in keywords:
                keyword_obj, created = ClassificationKeyword.objects.get_or_create(
                    category=category,
                    keyword=keyword
                )
                if created:
                    self.stdout.write(f'  ✓ 키워드 생성: {keyword}')
        
        # B 커머스 계정과목 및 키워드
        categories_b = [
            ('cat_201', '교통비', 'expense', ['카카오 T', '택시']),
            ('cat_202', '통신비', 'expense', ['KT', 'SKT']),
            ('cat_203', '지급수수료', 'expense', ['우체국', '등기']),
            ('cat_204', '복리후생비', 'expense', ['스타벅스']),
        ]
        
        for cat_id, cat_name, cat_type, keywords in categories_b:
            category, created = Category.objects.get_or_create(
                category_id=cat_id,
                defaults={
                    'company': company_b,
                    'category_name': cat_name,
                    'category_type': cat_type
                }
            )
            if created:
                self.stdout.write(f'✓ 계정과목 생성: {category.category_name}')
            
            for keyword in keywords:
                keyword_obj, created = ClassificationKeyword.objects.get_or_create(
                    category=category,
                    keyword=keyword
                )
                if created:
                    self.stdout.write(f'  ✓ 키워드 생성: {keyword}')
        
        self.stdout.write(
            self.style.SUCCESS('초기 데이터 생성이 완료되었습니다!')
        ) 