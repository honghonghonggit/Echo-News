"""WSGI config for echonews project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'echonews.settings') #Django가 사용할 설정 파일(settings.py)을 환경 변수로 지정합니다.

application = get_wsgi_application() #웹 서버가 요청을 받으면 이 application을 통해 Django 내부로 전달됩니다.
