from django.apps import AppConfig


class RequerimentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'requerimentos'

    def ready(self):
        import requerimentos.signals