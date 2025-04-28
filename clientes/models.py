from django.db import models


class Cliente(models.Model):
    cpf = models.CharField(max_length=11, primary_key=True)  # CPF e unico para cada cliente Ex: 12345678900
    nome = models.CharField(max_length=100)  # Nome do cliente Ex: Joao da Silva
    data_nascimento = models.DateField()  # Data de nascimento do cliente Ex: 21-01-1990
    telefone = models.CharField(max_length=11, blank=True, null=True)  # Telefone do cliente Ex: 81999998888
    observacao_telefone = models.TextField(blank=True, null=True)  # Observacao do telefone do cliente Ex: Recado Luiz
    telefone_whatsapp = models.CharField(max_length=11, blank=True, null=True)  # Telefone do cliente Ex: 81999998888
    email = models.EmailField(max_length=100, blank=True, null=True)  # Email do cliente Ex:

    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.cpf}, {self.nome}, {self.data_nascimento}, {self.telefone_whatsapp}, {self.telefone}, {self.email}'  # Retorna o nome do cliente e o CPF do cliente

    def get_class_name(self):
        return self.__class__.__name__

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    @property
    def total_requerimentos(self):
        from requerimentos.models import Requerimento

        lista_requerimentos = Requerimento.objects.filter(is_deleted=False).filter(
            requerente_titular=self
        )
        return len(lista_requerimentos)

    @property
    def total_atendimentos(self):
        from atendimentos.models import Atendimento

        lista_atendimentos = Atendimento.objects.filter(is_deleted=False).filter(
            cliente=self
        )
        return len(lista_atendimentos)
