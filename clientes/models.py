import datetime
from django.db import models


# Create your models here.
class Cliente(models.Model):
    cpf = models.CharField(max_length=11, primary_key =True) # CPF e unico para cada cliente Ex: 12345678900
    nome = models.CharField(max_length=100) # Nome do cliente Ex: Joao da Silva
    data_nascimento = models.DateField() # Data de nascimento do cliente Ex: 21-01-1990
    telefone = models.CharField(max_length=11, blank=True, null=True) # Telefone do cliente Ex: 81999998888
    observacao_telefone = models.TextField(blank=True, null=True) # Observacao do telefone do cliente Ex: Recado Luiz
    telefone_whatsapp = models.CharField(max_length=11, blank=True, null=True) # Telefone do cliente Ex: 81999998888
    email = models.EmailField(max_length=100, blank=True, null=True) # Email do cliente Ex:
    
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
        lista_atendimentos = Atendimento.objects.filter(is_deleted=False).filter(
            cliente=self
            )
        return len(lista_atendimentos)


class Atendimento(models.Model):
    from requerimentos.models import Requerimento
    
    id = models.AutoField(primary_key=True) # ID do atendimento
    data = models.DateTimeField() # Data do atendimento
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cliente_atendimento') # Relacionamento com o modelo Cliente
    requerimento = models.ForeignKey(Requerimento, on_delete=models.PROTECT, related_name='requerimento_atendimento', blank=True, null=True) # Relacionamento com o modelo Requerimento
    descricao = models.TextField(blank=True, null=True) # Descricao do atendimento
    observacao = models.TextField(blank=True, null=True) # Observacao do atendimento

    is_deleted = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f'Atendimento: id nº {self.id} de {self.cliente.nome}, {self.cliente.cpf}' # Retorna o nome do atendimento

'''
class Documento(models.Model):
    id = models.AutoField(primary_key=True) # ID do documento
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cliente_documento') # Relacionamento com o modelo Cliente
    arquivo = models.FileField(upload_to='documentos/') # Arquivo do documento
    nome_arquivo = models.CharField(max_length=100) # Nome do documento Ex: RG, CPF, Comprovante de residencia
    descricao = models.TextField(blank=True, null=True) # Descricao do documento
    requerimento = models.ForeignKey(Requerimento, on_delete=models.PROTECT, related_name='requerimento_documento', blank=True, null=True) # Relacionamento com o modelo Requerimento
    exigencia = models.ForeignKey(Exigencia, on_delete=models.PROTECT, related_name='exigencia_documento', blank=True, null=True) # Relacionamento com o modelo Exigencia

    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.nome_arquivo}' # Retorna o nome do documento
    
'''
