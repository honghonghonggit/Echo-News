from django.shortcuts import render
from django.db import IntegrityError

from .models import News
from .services import fetch_naver_news, fetch_og_image, _clean_html, _parse_pub_date


def news_list(request):
    """
    뉴스 검색 · 저장 · 목록 표시 뷰

    - GET ?q=검색어  → 네이버 API 호출 → og:image 추출 → DB 저장
    - GET ?sort=date  → 최신순 정렬 (기본값)
    - 이미 존재하는 링크는 중복 저장하지 않음
    """
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'date')
    message = ''

    # ── 검색어가 있을 때만 API 호출 ──
    if query:
        try:
            items = fetch_naver_news(query)
            saved = 0
            skipped = 0

            for item in items:
                title = _clean_html(item.get('title', ''))
                link = item.get('originallink') or item.get('link', '')
                description = _clean_html(item.get('description', ''))
                pub_date = _parse_pub_date(item.get('pubDate', ''))

                # 중복 링크 확인
                if News.objects.filter(link=link).exists():
                    skipped += 1
                    continue

                # og:image 썸네일 추출
                image_url = fetch_og_image(link)

                try:
                    News.objects.create(
                        title=title,
                        link=link,
                        description=description,
                        pub_date=pub_date,
                        image_url=image_url,
                    )
                    saved += 1
                except IntegrityError:
                    skipped += 1

            message = f'"{query}" 검색 완료 — 새로 저장: {saved}건, 중복 건너뜀: {skipped}건'
        except Exception as e:
            message = f'뉴스 가져오기 실패: {e}'

    # ── 정렬 ──
    if sort == 'date':
        news = News.objects.all().order_by('-pub_date')
    else:
        news = News.objects.all().order_by('-pub_date')

    context = {
        'news_list': news,
        'query': query,
        'sort': sort,
        'message': message,
    }
    return render(request, 'news/news_list.html', context)
