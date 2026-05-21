"""네이버 뉴스 API로 수집한 뉴스 데이터를 저장하는 모델 정의"""
from django.db import models


class News(models.Model):
    """네이버 뉴스 API로 수집한 뉴스 데이터를 저장하는 모델"""
    #기사를 클릭하기 전 보이는 기사 하나당 프론트엔드
    title = models.CharField(max_length=300, verbose_name='뉴스 제목')
    link = models.URLField(max_length=500, unique=True, verbose_name='원문 링크') #사용자 입장에선 안 보일 것
    description = models.TextField(verbose_name='뉴스 요약') #기사 클릭 전 보이는 기사 일부 내용
    pub_date = models.DateTimeField(verbose_name='발행일')
    image_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='썸네일 이미지 링크',
    ) #이미지를 불러올 수 있는 링크를 저장하는 것이므로 썸네일 이미지 링크를 저장해 둔 것
    views = models.IntegerField(default=0, verbose_name='조회수')
    reaction_count = models.IntegerField(default=0, verbose_name='반응 수')

    class Meta: #모델의 메타데이터(부가 설정)를 정의하는 내부 클래스입니다.
        verbose_name = '뉴스' #Admin 등에서 단수형 이름을 "뉴스"로 표시
        verbose_name_plural = '뉴스 목록' #복수형 이름을 "뉴스 목록"으로 표시
        ordering = ['-pub_date'] #기본 정렬을 발행일 내림차순(최신순)으로 지정

    def __str__(self):
        return self.title
