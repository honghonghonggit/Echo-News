from django.db import models


class News(models.Model):
    """네이버 뉴스 API로 수집한 뉴스 데이터를 저장하는 모델"""
    #네이버 뉴스 API로 크롤링한 기사의 제목, 요약, 썸네일 이미지를 최신순으로 가져오는 코드
    title = models.CharField(max_length=300, verbose_name='뉴스 제목')
    link = models.URLField(max_length=500, unique=True, verbose_name='원문 링크')
    description = models.TextField(verbose_name='뉴스 요약')
    pub_date = models.DateTimeField(verbose_name='발행일')
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='썸네일 이미지 링크',
    )
    views = models.IntegerField(default=0, verbose_name='조회수')
    reaction_count = models.IntegerField(default=0, verbose_name='반응 수')

    class Meta:
        #"관리자 화면에서 어떻게 표시할지"와 "기본 정렬을 어떻게 할지"를 지정한 클래스
        verbose_name = '뉴스' #기사가 한개일 때
        verbose_name_plural = '뉴스 목록' #기사가 여러개일 때
        ordering = ['-pub_date']

    def __str__(self):
        return self.title
