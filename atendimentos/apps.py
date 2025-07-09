from django.apps import AppConfig


class AtendimentosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'atendimentos'

    def ready(self):
        import atendimentos.signals
