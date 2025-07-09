from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from atendimentos.models import Atendimento


@receiver([post_save, post_delete], sender=Atendimento)
def invalidate_atendimento_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de atendimentos incrementando um número de versão.
    """
    try:
        cache.incr('atendimentos_list_version_html')
    except ValueError:
        pass  # A chave não existe, nada a fazer.

    try:
        cache.incr('atendimentos_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    # Incrementa as versões de cache para HTML e API
    # Isso garante que tanto as views da web quanto as da API buscarão
    # uma nova lista na próxima requisição, independentemente da ordenação.
    print(f"Versões de cache de atendimentos invalidadas devido a uma alteração no atendimento: {instance.id}")