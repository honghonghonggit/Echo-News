"""Django Admin에서 News 모델을 관리하기 위한 설정"""
from django.contrib import admin

from .models import News


@admin.register(News) #News 모델을 Django Admin에 등록합니다.
class NewsAdmin(admin.ModelAdmin):
    """Django Admin에서 뉴스 데이터를 편리하게 조회·관리하기 위한 설정"""

    list_display = ('title', 'pub_date', 'views') #admin 목록에  뉴스 제목(title), 발행일(pub_date), 조회수(views)를 표시함
    list_filter = ('pub_date',) #발행일(pub_date) 기준으로 필터링하는 기능 제공
    search_fields = ('title', 'description') #admin 검색창에서 제목(title)과 요약(description)으로 검색
    ordering = ('-pub_date',) #발행일 내림차순(-pub_date) → 최신 뉴스가 위에 표시됨.
