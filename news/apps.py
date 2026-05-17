from django.apps import AppConfig


class NewsConfig(AppConfig):
    """news 앱의 기본 설정 클래스"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news' #Django가 이 앱을 인식할 때 'news'라는 이름으로 등록합니다.

