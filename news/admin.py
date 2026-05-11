"""Django Admin에서 News 모델을 관리하기 위한 설정"""
from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Django Admin에서 뉴스 데이터를 편리하게 조회·관리하기 위한 설정"""

    list_display = ('title', 'pub_date', 'views')   # 목록에 표시할 필드
    list_filter = ('pub_date',)                      # 필터 사이드바 항목
    search_fields = ('title', 'description')         # 검색 대상 필드
    ordering = ('-pub_date',)                         # 기본 정렬 순서
