from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Django Admin에서 뉴스 데이터를 편리하게 조회·관리하기 위한 설정"""

    list_display = ('title', 'pub_date', 'views')
    list_filter = ('pub_date',)
    search_fields = ('title', 'description')
    ordering = ('-pub_date',)
