"""Django settings for echonews project."""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True #운영 환경에서는 반드시 False로 해야하는데, 안그러면 서버 내부 정보가 외부에 유출될 수 있음

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'news', #실행할 'news' 앱 등록
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'echonews.urls' #각 URL 패턴을 어떤 view 함수/클래스로 연결할지 설정한다.

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates', #어떤 템플릿 엔진을 쓸지 지정. 기본은 DjangoTemplates.
        'DIRS': [], #템플릿을 찾을 추가 디렉토리 목록.
        'APP_DIRS': True, #각 앱 내부의 templates/ 디렉토리를 자동으로 인식한다.
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'echonews.wsgi.application' # Django와 웹 서버 사이의 연결 다리 역할을 한다.

DATABASES = { #프로젝트에서 사용할 데이터베이스를 설정하는 구간
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [ #사용자 계정 비번 검증하는 구간인데, 지금은 쓰지 않으나 나중에 쓸 때를 대비해서 만들어 둔 것?
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' #모든 모델의 기본키 타입을 지정하는 부분

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID', '') #네이버 API 아이디
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET', '') #네이버 API 비밀키


#.env 파일 생성
#↓
#load_dotenv() 실행
#↓
#환경변수 등록
#↓
#os.getenv()로 읽기
#↓
#SECRET_KEY/API KEY 보호
