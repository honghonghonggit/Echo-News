"""echonews 프로젝트 루트 URL 설정"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),       # Django 관리자 페이지
    path('', include('news.urls')),         # news 앱 URL 위임
]
