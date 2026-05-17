"""echonews 프로젝트 루트 URL 설정"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls), # 관리자(Admin) 페이지 연결
    path('', include('news.urls')), # 사용자용 뉴스 앱 URL 연결
]
