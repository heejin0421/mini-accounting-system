from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'logs', views.ProcessingLogViewSet)

urlpatterns = [
    # 웹 페이지
    path('', views.dashboard, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('upload/', views.upload_file, name='upload_file'),
    
    # API 엔드포인트
    path('api/', include(router.urls)),
    path('api/summary/', views.api_summary, name='api_summary'),
    path('api/process/', views.api_process_accounting, name='api_process'),
] 