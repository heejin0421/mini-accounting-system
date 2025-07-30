# 미니 자동 회계 처리 시스템

Django 기반의 자동화된 은행 거래 내역 분류 및 회계 처리 시스템입니다.
하나의 은행 계좌에서 운영되는 여러 사업체의 거래 내역을 키워드 기반으로 자동 분류하고 회계 처리를 수행합니다.

## 시스템 구조

```
Frontend (Templates) ←→ Django (Views/API) ←→ SQLite Database
                              ↓
                        Django Admin
```

## 핵심 파일

```
task/
├── accounting/              # Django 앱
│   ├── models.py           # 데이터 모델
│   ├── views.py            # 뷰 및 API
│   ├── forms.py            # 파일 업로드 폼
│   └── admin.py            # 관리자 설정
├── templates/              # HTML 템플릿
├── bank_transactions.csv   # 샘플 데이터
├── rules.json             # 분류 규칙
└── run_django.sh          # 실행 스크립트
```

## 데이터 모델

- **Company**: 회사 정보
- **Category**: 계정과목
- **ClassificationKeyword**: 분류 키워드
- **Transaction**: 거래 내역
- **ProcessingLog**: 처리 로그

## 빠른 시작

```bash
# 실행 스크립트 (권장)
./run.sh

# 또는 수동 설정
python -m venv venv
source venv/bin/activate
pip install -r django_requirements.txt
python manage.py migrate
python manage.py init_data
python manage.py runserver
```

## 접속

- **웹 애플리케이션**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API**: http://localhost:8000/api/

## 어드민 계정 생성

Django Admin 페이지에 접속하려면 먼저 관리자 계정을 생성해야 합니다.

```bash
python manage.py createsuperuser
```

## 사용법

1. **파일 업로드**: CSV 파일 선택 후 업로드
2. **대시보드 확인**: 자동 분류 결과 및 요약 정보 확인
3. **관리자 기능**: Django Admin에서 데이터 관리

## API 엔드포인트

- `GET /api/transactions/` - 거래 내역 조회
- `GET /api/summary/` - 요약 정보 조회
- `GET /api/transactions/company/{id}/` - 회사별 조회
- `GET /api/transactions/category/{id}/` - 카테고리별 조회

## 보안

- **파일 검증**: CSV 형식, 10MB 제한
- **CSRF 보호**: Django Forms 기반
- **중복 방지**: 안전한 업로드 처리

## 기술 스택

- **Backend**: Django 4.2.7, Django REST Framework, SQLite, Pandas
- **Frontend**: Bootstrap 5, Jinja2 , jQuery
