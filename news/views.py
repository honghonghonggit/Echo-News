"""
뉴스 검색 · 저장 · 목록 표시 뷰 및 금융 지표 API 뷰
"""
import random

import requests
from django.shortcuts import render
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.cache import cache

from .models import News
from .services import fetch_naver_news, fetch_og_image, fetch_reaction_count, _clean_html, _parse_pub_date


# 검색어 미입력 시 랜덤으로 선택할 기본 키워드 목록
DEFAULT_KEYWORDS = ["미국", "경제", "스포츠", "세계", "날씨", "기술", "연예"]

# Yahoo Finance API 요청에 사용할 User-Agent 헤더
_YAHOO_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    ),
}

# 금융 지표 심볼 목록 (표시명, Yahoo Finance 심볼)
_TICKER_SYMBOLS = [
    ('나스닥', '^IXIC'),
    ('코스피', '^KS11'),
    ('코스닥', '^KQ11'),
    ('S&P 500', '^GSPC'),
    ('환율(USD/KRW)', 'KRW=X'),
]


def news_list(request):
    """
    뉴스 검색 · 저장 · 목록 표시 뷰

    - GET ?q=검색어  → 네이버 API 호출 → og:image 추출 → DB 저장
    - GET ?sort=date  → 최신순 정렬 (기본값)
    - GET ?sort=sim   → 유사도순(인기순) 정렬
    - 검색할 때마다 기존 DB 데이터를 삭제하고 새 결과만 저장
    """
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'date')

    # 키워드가 없으면 랜덤 키워드 자동 선택
    if not query:
        query = random.choice(DEFAULT_KEYWORDS)

    # API 호출 후 DB 갱신
    _fetch_and_save_news(query, sort)

    # 정렬 기준에 따라 뉴스 조회
    if sort == 'sim':
        news = News.objects.all().order_by('-reaction_count')  # 인기순
    else:
        news = News.objects.all().order_by('-pub_date')  # 최신순

    context = {
        'news_list': news,
        'query': query,
        'sort': sort,
    }
    return render(request, 'news/news_list.html', context)


def _fetch_and_save_news(query, sort):
    """
    네이버 API로 뉴스를 가져와 DB에 저장한다.
    기존 데이터를 모두 삭제한 뒤 새 결과만 저장한다.
    """
    try:
        items = fetch_naver_news(query, display=15, sort=sort)

        # 기존 DB 데이터 전부 삭제
        News.objects.all().delete()

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
            except IntegrityError:
                # 동일한 링크의 뉴스가 이미 존재하면 무시
                pass

    except Exception:
        # API 호출 실패 시 기존 DB 유지
        pass


def ticker_api(request):
    """
    Yahoo Finance 비공식 API를 사용하여 환율 및 주요 지수 데이터를 가져온다.
    API 제한을 고려하여 115초(약 2분)간 캐싱한다.
    """
    cache_key = 'yahoo_ticker_data'
    cached_data = cache.get(cache_key)
    if cached_data:
        return JsonResponse(cached_data)

    results = []

    for name, symbol in _TICKER_SYMBOLS:
        result = _fetch_single_ticker(name, symbol)
        if result:
            results.append(result)

    response_data = {'data': results}
    cache.set(cache_key, response_data, 115)
    return JsonResponse(response_data)


def _fetch_single_ticker(name, symbol):
    """
    Yahoo Finance에서 단일 지표 데이터를 가져온다.

    Args:
        name: 표시명 (예: '나스닥')
        symbol: Yahoo Finance 심볼 (예: '^IXIC')

    Returns:
        dict | None: 지표 데이터 딕셔너리. 실패 시 None 반환.
    """
    try:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo'
        res = requests.get(url, headers=_YAHOO_HEADERS, timeout=5)
        data = res.json()

        result_list = data.get('chart', {}).get('result', [])
        if not result_list:
            return None

        meta = result_list[0].get('meta', {})
        current = meta.get('regularMarketPrice')
        prev_close = meta.get('previousClose') or meta.get('chartPreviousClose')

        # 30일간 종가 히스토리 추출
        indicators = result_list[0].get('indicators', {})
        quote = indicators.get('quote', [{}])[0]
        close_prices = quote.get('close', [])
        history = [p for p in close_prices if p is not None]

        if current is not None:
            change_pct = ((current - prev_close) / prev_close * 100) if prev_close else 0
            return {
                'name': name,
                'price': f"{current:,.2f}",
                'change': round(change_pct, 2),
                'history': history,
            }
    except Exception:
        pass

    return None
