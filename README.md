# 🗞️ Echo News (실시간 뉴스 토픽 검색 엔진)

## 📌 프로젝트 소개
 
Echo News는 단국대학교 오픈소스SW기초 수업 팀 프로젝트로 개발된 실시간 뉴스 검색 엔진입니다.
사용자가 키워드를 입력하면 네이버 뉴스 API로 관련 기사를 실시간으로 수집하고,
BeautifulSoup4로 썸네일 이미지와 공감수를 크롤링하여 최신순/인기순으로 정렬해 제공합니다.
 
---
 
## 👥 팀원
 
| 이름 | 학번 | 역할 |
|------|------|------|
| 장세현 | 32223907 | 프론트 구현 |
| 홍성제 | 32225001 | 백엔드 구현 |
| 이규황 | 32223026 | 발표 담당 |
 
---
 
## 🔧 기술 스택
 
| 분류 | 기술 |
|------|------|
| 백엔드 | Python 3.11, Django 5.2 |
| 크롤링 | requests, BeautifulSoup4 |
| 데이터 수급 | 네이버 뉴스 검색 API |
| 날씨 | Open-Meteo API |
| 주식/환율 | Yahoo Finance 비공식 API |
| 프론트엔드 | Bootstrap 5, Chart.js |
| DB | SQLite |
| 보안 | python-dotenv |
| 협업 | Git / GitHub |
 
---
 
## 🗂️ 주요 기능
 
- 🔍 **키워드 검색** — 네이버 뉴스 API로 실시간 기사 15건 수집
- 🗂️ **카테고리 탭** — 미국, 경제, 스포츠, 세계, 날씨, 기술, 연예
- 🖼️ **썸네일 이미지** — og:image 메타태그 크롤링
- 🔃 **정렬 기능** — 최신순 / 공감수 기반 인기순
- 📄 **페이지네이션** — 5개씩 나눠서 표시
- ⭐ **북마크** — 기사 저장 및 사이드바 목록 표시
- 🌤️ **날씨 위젯** — 서울 실시간 날씨 (Open-Meteo)
- 📈 **주식/환율 티커** — 나스닥, 코스피, 코스닥, S&P500, 환율
- 🔮 **오늘의 운세** — 클릭 시 랜덤 운세 표시
- 🕐 **실시간 시계** — 오전/오후 포함 HH:MM:SS
---
 
## 📁 프로젝트 구조
 
```
Echo-News/
├── echonews/          # Django 프로젝트 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── news/              # 뉴스 앱
│   ├── models.py      # News 모델
│   ├── views.py       # 뷰 로직
│   ├── services.py    # API 호출 및 크롤링
│   ├── urls.py
│   └── templates/
│       └── news/
│           └── news_list.html
├── .env               # 환경변수 (git 제외)
├── .gitignore
├── manage.py
└── requirements.txt
```
 
---
 
## 🔗 참고 자료
 
- 네이버 개발자 센터: https://developers.naver.com
- Django 공식 문서: https://docs.djangoproject.com
- Open-Meteo API: https://open-meteo.com
- BeautifulSoup4 문서: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

---

## 🚀 시작하기

### 1. 레포지토리 클론
```bash
git clone https://github.com/honghonghonggit/Echo-News.git
cd Echo-News
```

### 2. 환경변수 설정
`.env.example`을 `.env`로 이름 변경 후 API 키를 입력해주세요.

> 네이버 API 키 발급: https://developers.naver.com

### 3. DB 마이그레이션 및 서버 실행
```bash
python manage.py migrate
python manage.py runserver
```

브라우저에서 http://127.0.0.1:8000 접속하면 끝!
