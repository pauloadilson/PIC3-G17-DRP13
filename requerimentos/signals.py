from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver

from agenda.models import Evento
from requerimentos.models import (
    RequerimentoInicial,
    RequerimentoRecurso,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
    HistoricoMudancaEstadoRequerimentoInicial,
    HistoricoMudancaEstadoRequerimentoRecurso
)


@receiver(post_save, sender=HistoricoMudancaEstadoRequerimentoInicial)
def registrar_mudanca_estado_requerimento_inicial(sender, instance, created, **kwargs):
    # Mudança de estado do requerimento inicial
    if created and instance.requerimento.get_class_name() == 'RequerimentoInicial':
        requerimento_inicial = instance.requerimento
        # Usar update() em vez de save() para evitar disparar signals desnecessários
        RequerimentoInicial.objects.filter(id=requerimento_inicial.id).update(estado=instance.estado_novo)
        # Atualizar a instância em memória também
        requerimento_inicial.estado = instance.estado_novo

        if instance.estado_novo.nome == 'concluído indeferido':
            # Criando evento Prazo para requerimento indeferido
            data_inicio = instance.data_mudanca + timedelta(days=30, hours=17)
            data_fim = data_inicio + timedelta(hours=1)
            Evento.objects.create(
                tipo='prazo',
                titulo=f'Prazo para o Requerimento nº {requerimento_inicial.NB} do Cliente {requerimento_inicial.requerente_titular.nome}, CPF nº {requerimento_inicial.requerente_titular.cpf}',
                descricao=f'Cliente {requerimento_inicial.requerente_titular.nome}, CPF nº {requerimento_inicial.requerente_titular.cpf}. Requerimento nº {requerimento_inicial.NB} concluído com indeferimento. Prazo para recurso.',
                data_inicio=data_inicio,
                data_fim=data_fim,
                local='Escritório'
            )


@receiver(post_save, sender=HistoricoMudancaEstadoRequerimentoRecurso)
def registrar_mudanca_estado_requerimento_recurso(sender, instance, created, **kwargs):
    # Mudança de estado do requerimento recurso
    if created and instance.requerimento.get_class_name() == 'RequerimentoRecurso':
        requerimento_recurso = instance.requerimento
        # Usar update() em vez de save() para evitar disparar signals desnecessários
        RequerimentoRecurso.objects.filter(id=requerimento_recurso.id).update(estado=instance.estado_novo)
        # Atualizar a instância em memória também
        requerimento_recurso.estado = instance.estado_novo

        if instance.estado_novo.nome == 'concluído indeferido':
            # Criando evento Prazo para recurso indeferido
            data_inicio = instance.data_mudanca + timedelta(days=30, hours=17)
            data_fim = data_inicio + timedelta(hours=1)
            Evento.objects.create(
                tipo='prazo',
                titulo=f'Prazo para o Requerimento nº {requerimento_recurso.NB} do Cliente {requerimento_recurso.requerente_titular.nome}, CPF nº {requerimento_recurso.requerente_titular.cpf}',
                descricao=f'Cliente {requerimento_recurso.requerente_titular.nome}, CPF nº {requerimento_recurso.requerente_titular.cpf}. Requerimento nº {requerimento_recurso.NB} concluído com indeferimento. Prazo para recurso.',
                data_inicio=data_inicio,
                data_fim=data_fim,
                local='Escritório'
            )


@receiver([post_save, post_delete], sender=RequerimentoInicial)
def invalidate_requerimento_inicial_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de requerimentos iniciais incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    try:
        cache.incr('requerimentos_iniciais_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de requerimentos iniciais invalidadas devido a uma alteração no requerimento inicial: {instance.id}")


@receiver([post_save, post_delete], sender=RequerimentoRecurso)
def invalidate_requerimento_recurso_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de recursos incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    try:
        cache.incr('requerimentos_recursos_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de recursos invalidadas devido a uma alteração no recurso: {instance.id}")


@receiver([post_save, post_delete], sender=ExigenciaRequerimentoInicial)
def invalidate_exigencia_requerimento_inicial_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de exigencias de requerimentos iniciais incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    try:
        cache.incr('exigencias_iniciais_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de exigencias de requerimentos iniciais invalidadas devido a uma alteração na exigência: {instance.id}")


@receiver([post_save, post_delete], sender=ExigenciaRequerimentoRecurso)
def invalidate_exigencia_requerimento_recurso_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de exigências de recursos incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    try:
        cache.incr('exigencias_recursos_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de exigências de recursos invalidadas devido a uma alteração na exigência: {instance.id}")


@receiver([post_save, post_delete], sender=HistoricoMudancaEstadoRequerimentoInicial)
def invalidate_historico_mudanca_estado_requerimento_inicial_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de mudanças de estado de requerimentos iniciais incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    try:
        cache.incr('mudancas_de_estado_iniciais_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de mudanças de estado de requerimentos iniciais invalidadas devido a uma alteração no histórico de mudança de estado: {instance.id}")


@receiver([post_save, post_delete], sender=HistoricoMudancaEstadoRequerimentoRecurso)
def invalidate_historico_mudanca_estado_requerimento_recurso_cache(sender, instance, **kwargs):
    """
    Invalida o cache da lista de mudanças de estado de recursos incrementando um número de versão.
    Isso garante que tanto as views da web quanto as da API buscarão
    uma nova lista na próxima requisição, independentemente da ordenação.
    """
    # Tenta incrementar as chaves. Se a chave não existir, alguns backends
    # (como o LocMemCache usado em testes) lançam um ValueError.
    # Nós o ignoramos, pois se a chave não existe, não há cache para invalidar.
    try:
        cache.incr('mudancas_de_estado_recursos_list_version_api')
    except ValueError:
        pass  # A chave não existe, nada a fazer.
    print(f"Versões de cache de mudanças de estado de recursos invalidadas devido a uma alteração no histórico de mudança de estado: {instance.id}")
