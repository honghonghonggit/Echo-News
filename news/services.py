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


# 크롤링 시 사용할 기본 HTTP 헤더 — 브라우저처럼 보이도록 설정하여 차단 방지
_CRAWL_HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    ),
}


def fetch_naver_news(query, display=15, sort='date'):
    """
    네이버 뉴스 검색 API를 호출하여 뉴스 데이터를 가져온다.

    Args:
        query: 검색 키워드
        display: 한 번에 가져올 뉴스 개수 (기본 15개)
        sort: 정렬 방식 — 'date'(최신순) 또는 'sim'(유사도순)

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
        'sort': sort,
    }

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()

    data = response.json()
    return data.get('items', [])


def _clean_html(text):
    """
    HTML 태그(<b>, </b> 등)를 제거하고 특수문자를 디코딩한다.
    사용자가 읽기 편한 텍스트로 변환하는 유틸리티 함수.
    """
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


def fetch_og_image(url):
    """
    기사 원문 링크에서 og:image 메타 태그의 썸네일 이미지 URL을 추출한다.

    Args:
        url: 기사 원문 링크

    Returns:
        str: og:image URL 문자열. 이미지가 없거나 오류 발생 시 빈 문자열 반환.
    """
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
    """
    네이버 뉴스 기사 URL에서 반응 수(공감/이모지 반응)를 크롤링한다.

    네이버 뉴스의 경우 반응 수 API(news.like.naver.com)를 호출하여
    좋아요·공감 등 이모지 반응 수의 합계를 반환한다.
    네이버 뉴스가 아닌 URL의 경우 BeautifulSoup으로 페이지를 파싱하여
    반응 수 영역을 찾는다.

    Args:
        url: 뉴스 기사 링크 (네이버 뉴스 URL 권장)

    Returns:
        int: 반응 수 합계. 가져오지 못하면 0 반환.
    """
    try:
        headers = {
            **_CRAWL_HEADERS,
            'Referer': 'https://n.news.naver.com',
        }

        # 네이버 뉴스 URL인 경우 반응 수 API 호출
        naver_count = _fetch_naver_reaction(url, headers)
        if naver_count is not None:
            return naver_count

        # 일반 URL: BeautifulSoup으로 반응 수 파싱
        return _fetch_general_reaction(url, headers)

    except Exception:
        return 0


def _fetch_naver_reaction(url, headers):
    """
    네이버 뉴스 URL에서 반응 수 API를 호출하여 반응 수를 반환한다.

    Args:
        url: 뉴스 기사 URL
        headers: HTTP 요청 헤더

    Returns:
        int | None: 반응 수. 네이버 뉴스 URL이 아니거나 실패 시 None 반환.
    """
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
    """
    일반 웹 페이지에서 반응 수를 CSS 셀렉터로 파싱하여 반환한다.

    Args:
        url: 뉴스 기사 URL
        headers: HTTP 요청 헤더

    Returns:
        int: 반응 수. 찾지 못하면 0 반환.
    """
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # 반응 수가 표시될 수 있는 CSS 셀렉터 목록
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
