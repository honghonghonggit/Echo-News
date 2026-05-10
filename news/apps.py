from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField' #models에 BigAutoField에 있는 데이터를 대입한다고 했는데 정작 github에는 models 디렉터리가 없는데?
    name = 'news'
