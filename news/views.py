from django.shortcuts import render

from .models import News
from .services import fetch_naver_news, save_news_to_db


def news_list(request):
    """
    뉴스 검색 · 저장 · 목록 표시 뷰

    - GET 파라미터 ?q=검색어  로 키워드 지정 (기본값: '미국')
    - 네이버 API에서 뉴스를 가져와 DB에 저장
    - 저장된 전체 뉴스를 최신순으로 보여줌
    """
    query = request.GET.get('q', '미국')

    # 네이버 API 호출 → DB 저장
    try:
        items = fetch_naver_news(query)
        saved, skipped = save_news_to_db(items)
        message = f'"{query}" 검색 완료 — 새로 저장: {saved}건, 중복 건너뜀: {skipped}건'
    except Exception as e:
        message = f'뉴스 가져오기 실패: {e}'

    # DB에 저장된 모든 뉴스 조회 (최신순)
    news = News.objects.all()

    context = {
        'news_list': news,
        'query': query,
        'message': message,
    }
    return render(request, 'news/news_list.html', context)
