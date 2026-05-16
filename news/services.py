"""
네이버 뉴스 API 호출 및 웹 크롤링 서비스 모듈

뉴스 데이터 수집에 필요한 외부 API 호출, HTML 파싱,
og:image 추출, 반응 수 크롤링 등의 기능을 제공한다.
"""
import re
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
from bs4 import BeautifulSoup
from django.conf import settings


_CRAWL_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
}


def fetch_naver_news(query, display=15, sort='date'):
    """네이버 뉴스 검색 API를 호출하여 뉴스 아이템 리스트를 반환한다."""
    url = 'https://openapi.naver.com/v1/search/news.json'
    headers = {
        'X-Naver-Client-Id': settings.NAVER_CLIENT_ID,
        'X-Naver-Client-Secret': settings.NAVER_CLIENT_SECRET,
    }
    params = {
        'query': query,
        'display': display,
        'sort': sort,
    }

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()

    data = response.json()
    return data.get('items', [])


def clean_html(text):
    """HTML 태그를 제거하고 특수문자를 디코딩한다."""
    text = re.sub(r'<.*?>', '', text)
    text = text.replace('&quot;', '"')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&apos;', "'")
    return text.strip()


def parse_pub_date(date_str):
    """RFC 2822 형식의 pubDate 문자열을 datetime 객체로 변환한다."""
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return datetime.now()


def fetch_og_image(url):
    """기사 원문 링크에서 og:image 메타 태그의 썸네일 URL을 추출한다."""
    try:
        response = requests.get(url, headers=_CRAWL_HEADERS, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        og_tag = soup.find('meta', property='og:image')

        if og_tag and og_tag.get('content'):
            return og_tag['content']

        return ''
    except Exception:
        return ''


def fetch_reaction_count(url):
    """네이버 뉴스 기사 URL에서 반응 수(공감/이모지)를 크롤링한다."""
    try:
        headers = {
            **_CRAWL_HEADERS,
            'Referer': 'https://n.news.naver.com',
        }

        naver_count = _fetch_naver_reaction(url, headers)
        if naver_count is not None:
            return naver_count

        return _fetch_general_reaction(url, headers)

    except Exception:
        return 0


def _fetch_naver_reaction(url, headers):
    """네이버 뉴스 반응 수 API를 호출하여 반응 수를 반환한다. 비네이버 URL이면 None."""
    naver_match = re.search(
        r'n\.news\.naver\.com/(?:mnews/)?article/(\d+)/(\d+)', url
    )
    if not naver_match:
        return None

    oid, aid = naver_match.group(1), naver_match.group(2)
    api_url = 'https://news.like.naver.com/v1/search/contents'
    api_params = {
        'suppress': 'true',
        'q': f'NEWS[ne_{oid}_{aid}]',
    }
    resp = requests.get(api_url, headers=headers, params=api_params, timeout=5)
    data = resp.json()

    contents = data.get('contents', [])
    if contents:
        reactions = contents[0].get('reactions', [])
        return sum(r.get('count', 0) for r in reactions)

    return 0


def _fetch_general_reaction(url, headers):
    """일반 웹 페이지에서 CSS 셀렉터로 반응 수를 파싱하여 반환한다."""
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    selectors = [
        'span.u_likeit_text._count',
        'em.u_cnt._count',
        'span.like_count',
    ]
    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            digits = re.sub(r'[^\d]', '', tag.get_text())
            if digits:
                return int(digits)

    return 0
