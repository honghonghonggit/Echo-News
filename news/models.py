from django.db import models


class News(models.Model):
    """네이버 뉴스 API로 수집한 뉴스 데이터를 저장하는 모델"""

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

    class Meta:
        verbose_name = '뉴스'
        verbose_name_plural = '뉴스 목록'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title
