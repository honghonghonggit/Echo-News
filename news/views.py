import random

from django.shortcuts import render
from django.db import IntegrityError

from .models import News
from .services import fetch_naver_news, fetch_og_image, fetch_reaction_count, _clean_html, _parse_pub_date


def news_list(request):
    """
    뉴스 검색 · 저장 · 목록 표시 뷰

    - GET ?q=검색어  → 네이버 API 호출 → og:image 추출 → DB 저장
    - GET ?sort=date  → 최신순 정렬 (기본값)
    - GET ?sort=sim   → 유사도순(인기순) 정렬
    - 검색할 때마다 기존 DB 데이터를 삭제하고 새 결과만 저장
    """
    DEFAULT_KEYWORDS = ["미국", "경제", "스포츠", "세계", "날씨", "기술", "연예"]

    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'date')


    # ── 키워드가 없으면 랜덤 키워드 자동 선택 ──
    if not query:
        query = random.choice(DEFAULT_KEYWORDS)

    # ── API 호출 ──
    if query:
        try:
            items = fetch_naver_news(query, display=15, sort=sort)

            # 기존 DB 데이터 전부 삭제
            News.objects.all().delete()

            saved = 0

            for item in items:
                title = _clean_html(item.get('title', ''))
                link = item.get('originallink') or item.get('link', '')
                description = _clean_html(item.get('description', ''))
                pub_date = _parse_pub_date(item.get('pubDate', ''))

                # og:image 썸네일 추출
                image_url = fetch_og_image(link)

                # 반응 수(공감/이모지) 크롤링
                naver_link = item.get('link', '')
                reaction_count = fetch_reaction_count(naver_link)

                try:
                    News.objects.create(
                        title=title,
                        link=link,
                        description=description,
                        pub_date=pub_date,
                        image_url=image_url,
                        reaction_count=reaction_count,
                    )
                    saved += 1
                except IntegrityError:
                    pass

        except Exception as e:
            pass

    # ── 정렬 ──
    if sort == 'sim':
        # 인기순: 반응 수 내림차순
        news = News.objects.all().order_by('-reaction_count')
    else:
        # 최신순: 발행일 내림차순
        news = News.objects.all().order_by('-pub_date')

    context = {
        'news_list': news,
        'query': query,
        'sort': sort,

    }
    return render(request, 'news/news_list.html', context)
