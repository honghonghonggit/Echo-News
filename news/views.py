"""뉴스 검색 · 저장 · 목록 표시 뷰 및 금융 지표 API 뷰"""
import random

import requests
from django.shortcuts import render
from django.db import IntegrityError
from django.http import JsonResponse
from django.core.cache import cache

from .models import News
from .services import (
    fetch_naver_news, fetch_og_image, fetch_reaction_count,
    clean_html, parse_pub_date, _CRAWL_HEADERS,
)


DEFAULT_KEYWORDS = ["미국", "경제", "스포츠", "세계", "날씨", "기술", "연예"]

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

    - GET ?q=검색어  → 네이버 API 호출 → DB 저장
    - GET ?sort=date → 최신순 (기본값), sort=sim → 인기순
    - 검색할 때마다 기존 DB를 삭제하고 새 결과만 저장
    """
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'date')

    if not query:
        query = random.choice(DEFAULT_KEYWORDS)

    _fetch_and_save_news(query, sort)

    if sort == 'sim':
        news = News.objects.all().order_by('-reaction_count')
    else:
        news = News.objects.all().order_by('-pub_date')

    context = {
        'news_list': news,
        'query': query,
        'sort': sort,
    }
    return render(request, 'news/news_list.html', context)


def _fetch_and_save_news(query, sort):
    """네이버 API로 뉴스를 가져와 DB에 저장한다. 기존 데이터는 모두 삭제."""
    try:
        items = fetch_naver_news(query, display=15, sort=sort)

        News.objects.all().delete()

        for item in items:
            title = clean_html(item.get('title', ''))
            link = item.get('originallink') or item.get('link', '')
            description = clean_html(item.get('description', ''))
            pub_date = parse_pub_date(item.get('pubDate', ''))

            image_url = fetch_og_image(link)

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
                pass

    except Exception:
        pass


def ticker_api(request):
    """Yahoo Finance 비공식 API로 환율·주요 지수 데이터를 반환한다. 115초 캐싱."""
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
    """Yahoo Finance에서 단일 지표 데이터를 가져온다. 실패 시 None."""
    try:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo'
        res = requests.get(url, headers=_CRAWL_HEADERS, timeout=5)
        data = res.json()

        result_list = data.get('chart', {}).get('result', [])
        if not result_list:
            return None

        meta = result_list[0].get('meta', {})
        current = meta.get('regularMarketPrice')
        prev_close = meta.get('previousClose') or meta.get('chartPreviousClose')

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
