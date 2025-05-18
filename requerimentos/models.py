from django.db import models
from clientes.models import Cliente


class Servico(models.Model):
    id = models.AutoField(primary_key=True)  # ID do serviço
    nome = models.CharField(max_length=100)  # Nome do serviço Ex: Aposentadoria por idade, Aposentadoria por invalidez

    def __str__(self) -> str:
        return f'{self.nome}'  # Retorna o nome do serviço


class Requerimento(models.Model):
    id = models.AutoField(primary_key=True)  # ID do requerimento
    protocolo = models.CharField(max_length=20, unique=True)  # Protocolo do requerimento
    NB = models.CharField(max_length=20, blank=True, null=True)  # Numero do benefi­cio do cliente
    requerente_titular = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cliente_titular_requerimento')  # Relacionamento com o modelo Cliente
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT, related_name='servico_requerimento')  # Servico solicitado Ex: Aposentadoria por idade
    requerente_dependentes = models.TextField(blank=True, null=True)  # .ManyToManyField(Cliente, related_name='cliente_dependente_requerimento', blank=True, null=True) # Relacionamento com o modelo Cliente
    tutor_curador = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cliente_tutor_curador_requerimento', blank=True, null=True)  # Relacionamento com o modelo Cliente
    instituidor = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='cliente_instituidor_requerimento', blank=True, null=True)  # Relacionamento com o modelo Cliente
    data = models.DateField()  # Data do requerimento
    email = models.EmailField(max_length=100, blank=True, null=True)  # Email do requerente na data do requerimento. Não atualiza o cadastrado no cliente
    observacao = models.TextField(blank=True, null=True)  # Observacoes do requerimento

    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'Requerimento de NB nº {self.NB} para {self.servico.nome}: {self.requerente_titular.nome}, {self.requerente_titular.cpf}, {self.requerente_titular.data_nascimento}'  # Retorna o nome do cliente e a data do requerimento

    def get_class_name(self):
        return self.__class__.__name__

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


class EstadoRequerimentoInicial(models.Model):
    ESTADOS_INICIAIS = [
        ('em análise', 'Em Análise'),
        ('aguardando cumprimento de exigência', 'Aguardando Cumprimento de Exigência'),
        ('concluído deferido', 'Concluído Deferido'),
        ('concluído indeferido', 'Concluído Indeferido'),
    ]

    id = models.AutoField(primary_key=True)  # ID do estado
    nome = models.CharField(max_length=100, choices=ESTADOS_INICIAIS)  # Nome do estado Ex: Em exigencia, Em analise, Conclui­do

    def __str__(self) -> str:
        return f'{self.nome}'  # Retorna o nome do estado


class RequerimentoInicial(Requerimento):
    estado = models.ForeignKey(EstadoRequerimentoInicial, on_delete=models.PROTECT, related_name='estado_requerimento_inicial')  # Estado do requerimento Ex: Pendente, Concluido

    @property
    def total_exigencias(self):
        lista_exigencias = ExigenciaRequerimentoInicial.objects.filter(is_deleted=False).filter(
            requerimento=self)
        return len(lista_exigencias)

    @property
    def total_mudancas_estado(self):
        lista_mudancas_estado = HistoricoMudancaEstadoRequerimentoInicial.objects.filter(requerimento=self)
        return len(lista_mudancas_estado)


class EstadoRequerimentoRecurso(models.Model):
    ESTADOS_RECURSOS = [
        ('em análise na junta', 'Em Análise na Junta'),
        ('em análise no conselho', 'Em Análise no Conselho'),
        ('concluído deferido', 'Concluído Deferido'),
        ('concluído indeferido', 'Concluído Indeferido'),
    ]

    id = models.AutoField(primary_key=True)  # ID do estado
    nome = models.CharField(max_length=30, choices=ESTADOS_RECURSOS)

    def __str__(self) -> str:
        return f'{self.nome}'


class RequerimentoRecurso(Requerimento):
    estado = models.ForeignKey(EstadoRequerimentoRecurso, on_delete=models.PROTECT, related_name='estado_requerimento_recurso')  # Estado do requerimento Ex: Em analise, Concluido

    @property
    def total_exigencias(self):
        lista_exigencias = ExigenciaRequerimentoRecurso.objects.filter(is_deleted=False).filter(
            requerimento=self
        )
        return len(lista_exigencias)

    @property
    def total_mudancas_estado(self):
        lista_mudancas_estado = HistoricoMudancaEstadoRequerimentoRecurso.objects.filter(requerimento=self)
        return len(lista_mudancas_estado)


class EstadoExigencia(models.Model):
    ESTADOS_EXIGENCIA = [
        ('em análise', 'Em Análise'),
        ('concluído', 'Concluído'),
    ]

    id = models.AutoField(primary_key=True)  # ID do estado
    nome = models.CharField(max_length=100, choices=ESTADOS_EXIGENCIA)  # Nome do estado Ex: Em exigencia, Em analise, Conclui­do

    def __str__(self) -> str:
        return f'{self.nome}'  # Retorna o nome do estado


class Natureza(models.Model):
    id = models.AutoField(primary_key=True)  # ID da natureza
    nome = models.CharField(max_length=100)  # Nome da natureza Ex: Documentacao, Informacao

    def __str__(self) -> str:
        return f'{self.nome}'  # Retorna o nome da natureza


class Exigencia(models.Model):
    id = models.AutoField(primary_key=True)  # ID da exigÃªncia
    data = models.DateField()  # Data da exigÃªncia
    natureza = models.ForeignKey(Natureza, on_delete=models.PROTECT, related_name='natureza_exigencia')  # Natureza da exigecia Ex: Documentacao, Informacao
    estado = models.ForeignKey(EstadoExigencia, on_delete=models.PROTECT, related_name='estado_exigencia')  # Estado do recurso Ex: Pendente, Conclui­do

    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        pass

    def get_class_name(self):
        return self.__class__.__name__

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


class ExigenciaRequerimentoInicial(Exigencia):
    # herdar de Exigencia
    requerimento = models.ForeignKey(RequerimentoInicial, on_delete=models.PROTECT, related_name='requerimento_inicial_exigencia')  # Relacionamento com o modelo Requerimento

    def __str__(self) -> str:
        return f'Exigência: id nº {self.id} do NB nº {self.requerimento.NB} de {self.requerimento.requerente_titular.nome}, {self.requerimento.requerente_titular.cpf}'


class ExigenciaRequerimentoRecurso(Exigencia):
    # herdar de Exigencia
    requerimento = models.ForeignKey(RequerimentoRecurso, on_delete=models.PROTECT, related_name='requerimento_recurso_exigencia')  # Relacionamento com o modelo Requerimento

    def __str__(self) -> str:
        return f'Exigência: id nº {self.id} do NB nº {self.requerimento.NB} de {self.requerimento.requerente_titular.nome}, {self.requerimento.requerente_titular.cpf}'


class HistoricoMudancaEstadoRequerimentoInicial(models.Model):
    id = models.AutoField(primary_key=True)  # ID do historico de estado do requerimento
    requerimento = models.ForeignKey(RequerimentoInicial, on_delete=models.PROTECT, related_name='historico_estado_requerimento')
    estado_anterior = models.ForeignKey(EstadoRequerimentoInicial, on_delete=models.SET_NULL, null=True, related_name='estado_anterior')
    estado_novo = models.ForeignKey(EstadoRequerimentoInicial, on_delete=models.PROTECT, related_name='estado_novo')
    observacao = models.TextField(blank=True, null=True)
    data_mudanca = models.DateTimeField()

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.requerimento.protocolo} do estado {self.estado_anterior.nome} para {self.estado_novo.nome} em {self.data_mudanca}"


class HistoricoMudancaEstadoRequerimentoRecurso(models.Model):
    id = models.AutoField(primary_key=True)  # ID do historico de estado do requerimento
    requerimento = models.ForeignKey(RequerimentoRecurso, on_delete=models.PROTECT, related_name='historico_estado_requerimento')
    estado_anterior = models.ForeignKey(EstadoRequerimentoRecurso, on_delete=models.SET_NULL, null=True, related_name='estado_anterior')
    estado_novo = models.ForeignKey(EstadoRequerimentoRecurso, on_delete=models.PROTECT, related_name='estado_novo')
    observacao = models.TextField(blank=True, null=True)
    data_mudanca = models.DateTimeField()

    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.requerimento.protocolo} do estado {self.estado_anterior.nome} para {self.estado_novo.nome} em {self.data_mudanca}"
