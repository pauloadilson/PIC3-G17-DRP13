from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from clientes.models import Cliente


@receiver([post_save, post_delete], sender=Cliente)
def invalidate_cliente_cache(sender, instance, **kwargs):
    """
    Invalida (deleta) o cache da lista de clientes sempre que um cliente
    é criado, atualizado ou deletado.
    """
    cache_key = 'lista_de_clientes'
    cache.delete(cache_key)
    print(f"Cache '{cache_key}' invalidado devido a uma alteração no cliente: {instance.nome}")
