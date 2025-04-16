from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

from agenda.models import Evento
from requerimentos.models import HistoricoMudancaEstadoRequerimentoInicial, HistoricoMudancaEstadoRequerimentoRecurso


@receiver(post_save, sender=HistoricoMudancaEstadoRequerimentoInicial)
def registrar_mudanca_estado_requerimento_inicial(sender, instance, created, **kwargs):
    # Mudança de estado do requerimento inicial
    if instance.requerimento.get_class_name() == 'RequerimentoInicial':
        requerimento_inicial = instance.requerimento
        requerimento_inicial.estado = instance.estado_novo
        requerimento_inicial.save()

        if requerimento_inicial.estado.nome == 'concluído indeferido':
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
    if instance.requerimento.get_class_name() == 'RequerimentoRecurso':
        requerimento_recurso = instance.requerimento
        requerimento_recurso.estado = instance.estado_novo
        requerimento_recurso.save()

        if requerimento_recurso.estado.nome == 'concluído indeferido':
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
