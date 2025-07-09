from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from clientes.models import Cliente


@receiver([post_save, post_delete], sender=Cliente)
def invalidate_cliente_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de clientes incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    # Tenta incrementar as chaves. Se a chave não existir, alguns backends
    # (como o LocMemCache usado em testes) lançam um ValueError.
    # Nós o ignoramos, pois se a chave não existe, não há cache para invalidar.
    try:
        cache.incr('clientes_list_version_html')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    try:
        cache.incr('clientes_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de clientes invalidadas devido a uma alteração no cliente: {instance.nome}")
