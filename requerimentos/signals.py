from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

from agenda.models import Evento
from requerimentos.models import HistoricoMudancaEstadoRequerimentoInicial


@receiver(post_save, sender=HistoricoMudancaEstadoRequerimentoInicial)
def registrar_mudanca_estado_requerimento_inicial(sender, instance, created, **kwargs):
    requerimento_inicial = instance.requerimento
    if instance.requerimento.get_class_name() == 'RequerimentoInicial':
        print('\nRecebendo sinal de mudança de estado de requerimento inicial')
        print(f'Estado anterior do requerimento inicial: {requerimento_inicial.estado}.')
        requerimento_inicial.estado = instance.estado_novo
        requerimento_inicial.save()
        print('Estado do requerimento inicial atualizado')
        print(f'Estado novo do requerimento inicial: {requerimento_inicial.estado}')
    if requerimento_inicial.estado.nome == 'concluído indeferido':
        print('Recebendo sinal de novo estado concluído indeferido')
        # Criando evento Prazo para recurso indeferido
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
        print('Evento criado para o prazo de recurso indeferido')
