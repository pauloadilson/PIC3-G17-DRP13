from django.db import models
from requerimentos.models import Requerimento
from clientes.models import Cliente


class Atendimento(models.Model):

    id = models.AutoField(primary_key=True)  # ID do atendimento
    data = models.DateTimeField()  # Data do atendimento
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='cliente_atendimento')  # Relacionamento com o modelo Cliente
    requerimento = models.ForeignKey(
        Requerimento,
        on_delete=models.PROTECT,
        related_name='requerimento_atendimento',
        blank=True,
        null=True)  # Relacionamento com o modelo Requerimento
    descricao = models.TextField(blank=True, null=True)  # Descricao do atendimento
    observacao = models.TextField(blank=True, null=True)  # Observacao do atendimento

    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Atendimento: id nº {self.id} de {self.cliente.nome}, {self.cliente.cpf}'
