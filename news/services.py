import requests
from datetime import datetime
from email.utils import parsedate_to_datetime

from django.conf import settings
from django.db import IntegrityError

from .models import News


def fetch_naver_news(query, display=10):
    """
    네이버 뉴스 검색 API를 호출하여 뉴스 데이터를 가져온다.

    Args:
        query: 검색 키워드
        display: 한 번에 가져올 뉴스 개수 (기본 10개)

    Returns:
        list[dict]: API에서 반환된 뉴스 아이템 리스트
    """
    url = 'https://openapi.naver.com/v1/search/news.json'
    headers = {
        'X-Naver-Client-Id': settings.NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': settings.NAVER_CLIENT_SECRET,
    }
    params = {
        'query': query,
        'display': display,
        'sort': 'date',  # 최신순 정렬
    }

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()

    data = response.json()
    return data.get('items', [])


def _clean_html(text):
    """HTML 태그(<b>, </b> 등)를 제거하고 특수문자를 디코딩한다."""
    import re
    text = re.sub(r'<.*?>', '', text)
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&apos;', "'")
    return text.strip()


def _parse_pub_date(date_str):
    """
    네이버 API의 pubDate 문자열(RFC 2822 형식)을 datetime 객체로 변환한다.
    예: 'Thu, 01 May 2026 09:00:00 +0900'
    """
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now()


def save_news_to_db(items):
    """
    API에서 받은 뉴스 아이템 리스트를 News 모델에 저장한다.
    동일한 link가 이미 존재하면 중복 저장하지 않는다.

    Args:
        items: fetch_naver_news()에서 반환된 아이템 리스트

    Returns:
        tuple(int, int): (새로 저장된 수, 중복으로 건너뛴 수)
    """
    saved = 0
    skipped = 0

    for item in items:
        title = _clean_html(item.get('title', ''))
        link = item.get('originallink') or item.get('link', '')
        description = _clean_html(item.get('description', ''))
        pub_date = _parse_pub_date(item.get('pubDate', ''))

        try:
            News.objects.create(
                title=title,
                link=link,
                description=description,
                pub_date=pub_date,
            )
            saved += 1
        except IntegrityError:
            # link가 unique이므로 중복 뉴스는 건너뜀
            skipped += 1

    return saved, skipped


def fetch_og_image(url):
    """
    기사 원문 링크에서 og:image 메타 태그의 썸네일 이미지 URL을 추출한다.

    Args:
        url: 기사 원문 링크

    Returns:
        str: og:image URL 문자열. 이미지가 없거나 오류 발생 시 빈 문자열 반환.
    """
    try:
        from bs4 import BeautifulSoup

        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        }

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        og_tag = soup.find('meta', property='og:image')

        if og_tag and og_tag.get('content'):
            return og_tag['content']

        return ''
    except Exception:
        return ''
