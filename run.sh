#!/bin/bash

echo "가상환경을 활성화합니다..."

# 가상환경이 없으면 생성
if [ ! -d "venv" ]; then
    echo "가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

echo "의존성을 설치합니다..."
pip install -r requirements.txt

echo "데이터베이스를 초기화합니다..."
python manage.py makemigrations
python manage.py migrate

echo "초기 데이터를 설정합니다..."
python manage.py init_data

echo "개발 서버를 시작합니다..."
echo "브라우저에서 http://localhost:8000 으로 접속하세요."
echo "종료하려면 Ctrl+C를 누르세요."
python manage.py runserver 