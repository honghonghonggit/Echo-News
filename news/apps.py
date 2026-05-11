from django.apps import AppConfig


class NewsConfig(AppConfig):
    """news 앱의 기본 설정 클래스"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'
