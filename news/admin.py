from django.contrib import admin

from .models import News


@admin.register(News) #News 모델을 Django Admin에 등록한다.
class NewsAdmin(admin.ModelAdmin):
    """Django Admin에서 뉴스 데이터를 편리하게 조회·관리하기 위한 설정"""

    list_display = ('title', 'pub_date', 'views') #맨 위 사이트 제목
    list_filter = ('pub_date',) #특정 날짜 기준의 기사만 가져
    search_fields = ('title', 'description') #기사 제목과 일부 내용을 출력
    ordering = ('-pub_date',) #기사가 최근에 나온 것 위주로 게시한다.
