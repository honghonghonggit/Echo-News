"""news 앱 URL 라우팅 설정"""
from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='news_list'),
    path('api/ticker/', views.ticker_api, name='ticker_api'),
]
