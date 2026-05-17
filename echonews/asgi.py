"""ASGI config for echonews project."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echonews.settings') #Django가 사용할 설정 파일(settings.py)을 환경 변수로 지정합니다.

application = get_asgi_application() # 클라이언트 요청이 들어오면 ASGI 서버가 이 application을 통해 Django 내부로 전달합니다.
