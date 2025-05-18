from django.test import TransactionTestCase
import uuid
from django.urls import reverse, resolve
from django.utils import timezone

from clientes.models import Cliente
from requerimentos.models import (
    EstadoExigencia,
    EstadoRequerimentoInicial,
    ExigenciaRequerimentoInicial,
    HistoricoMudancaEstadoRequerimentoInicial,
    Natureza,
    RequerimentoInicial,
    Servico,
    EstadoRequerimentoRecurso,
    RequerimentoRecurso,
    ExigenciaRequerimentoRecurso,
)


def generate_unique_cpf():
    return str(uuid.uuid4().int)[:11]


def generate_unique_protocolo():
    return str(uuid.uuid4().int)[:15]


class TestUrls(TransactionTestCase):
    def setUp(self) -> None:
        # Common objects
        self.cpf = generate_unique_cpf()
        self.cliente = Cliente.objects.create(
            cpf=self.cpf,
            nome="Teste Cliente",
            data_nascimento="1990-01-01",
            telefone_whatsapp="1234567890",
            email="teste@cliente.com",
        )
        self.servico = Servico.objects.create(
            nome="Aposentadoria por Idade Urbana"
        )

        # Objects for requerimento_inicial
        self.estado_inicial = EstadoRequerimentoInicial.objects.create(
            nome="em análise"
        )
        self.protocolo_inicial = generate_unique_protocolo()
        self.requerimento_inicial = RequerimentoInicial.objects.create(
            requerente_titular=self.cliente,
            protocolo=self.protocolo_inicial,
            NB="456123456123456123",
            servico=self.servico,
            data="2021-01-01",
            estado=self.estado_inicial,
        )

        # Objects for requerimento_recurso
        self.estado_recurso = EstadoRequerimentoRecurso.objects.create(
            nome="em análise na junta"
        )
        self.protocolo_recurso = generate_unique_protocolo()
        self.requerimento_recurso = RequerimentoRecurso.objects.create(
            requerente_titular=self.cliente,
            protocolo=self.protocolo_recurso,
            NB="321098765432109876",
            servico=self.servico,
            data="2021-02-01",
            estado=self.estado_recurso,
        )
        # Objects for exigencias
        self.natureza = Natureza.objects.create(nome="Documentação")
        self.estado_exigencia = EstadoExigencia.objects.create(nome="em análise")

    def test_adicionar_requerimento_inicial_url_resolves(self):
        url = reverse("adicionar_requerimento_inicial", kwargs={'cpf': self.cliente.cpf})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialCreateView")

    def test_requerimento_detail_url_resolves(self):
        url = reverse("requerimento_inicial", kwargs={'cpf': self.cliente.cpf, 'pk': self.requerimento_inicial.id})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialDetailView")

    def test_adicionar_exigencia_requerimento_inicial_url_resolves(self):
        url = reverse("adicionar_exigencia_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialCreateView")

    def test_atualizar_requerimento_inicial_url_resolves(self):
        url = reverse("atualizar_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialUpdateView")

    def test_excluir_requerimento_inicial_url_resolves(self):
        url = reverse("excluir_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialDeleteView")

    def test_ciencia_requerimento_inicial_url_resolves(self):
        url = reverse("ciencia_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "MudancaEstadoRequerimentoInicialCreateView")

    def test_excluir_mudanca_estado_requerimento_inicial_url_resolves(self):
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Deferido")

        historico = HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.requerimento_inicial.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        url = reverse("excluir_mudanca_estado_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id,
            "hist_pk": historico.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "MudancaEstadoRequerimentoInicialDeleteView")

    def test_adicionar_requerimento_recurso_url_resolves(self):
        url = reverse("adicionar_requerimento_recurso", kwargs={'cpf': self.cliente.cpf})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoCreateView")

    def test_requerimento_recurso_detail_url_resolves(self):
        url = reverse("requerimento_recurso", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_recurso.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoDetailView")

    def test_atualizar_requerimento_recurso_url_resolves(self):
        url = reverse("atualizar_requerimento_recurso", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_recurso.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoUpdateView")

    def test_excluir_requerimento_recurso_url_resolves(self):
        url = reverse("excluir_requerimento_recurso", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_recurso.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoDeleteView")

    def test_atualizar_exigencia_requerimento_inicial_url_resolves(self):
        exigencia_inicial = ExigenciaRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            data="2021-01-10",
            natureza=self.natureza,  # Assumes a Natureza instance with id=1 exists or use a dummy integer if not used in view tests
            estado=self.estado_exigencia,    # Assumes EstadoExigencia instance with id=1 exists
        )

        url = reverse("atualizar_exigencia_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id,
            'exigencia_pk': exigencia_inicial.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialUpdateView")

    def test_excluir_exigencia_requerimento_inicial_url_resolves(self):
        exigencia_inicial = ExigenciaRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            data="2021-01-10",
            natureza=self.natureza,  # Assumes a Natureza instance with id=1 exists or use a dummy integer if not used in view tests
            estado=self.estado_exigencia,    # Assumes EstadoExigencia instance with id=1 exists
        )
        url = reverse("excluir_exigencia_requerimento_inicial", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_inicial.id,
            'exigencia_pk': exigencia_inicial.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialDeleteView")

    def test_adicionar_exigencia_requerimento_recurso_url_resolves(self):
        url = reverse("adicionar_exigencia_requerimento_recurso", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_recurso.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoRecursoCreateView")

    def test_atualizar_exigencia_requerimento_recurso_url_resolves(self):
        exigencia_recurso = ExigenciaRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            data="2021-02-10",
            natureza=self.natureza,
            estado=self.estado_exigencia,
        )
        url = reverse("atualizar_exigencia_requerimento_recurso", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_recurso.id,
            'exigencia_pk': exigencia_recurso.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoRecursoUpdateView")

    def test_excluir_exigencia_requerimento_recurso_url_resolves(self):
        exigencia_recurso = ExigenciaRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            data="2021-02-10",
            natureza=self.natureza,
            estado=self.estado_exigencia,
        )
        url = reverse("excluir_exigencia_requerimento_recurso", kwargs={
            'cpf': self.cliente.cpf,
            'pk': self.requerimento_recurso.id,
            'exigencia_pk': exigencia_recurso.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoRecursoDeleteView")

    def test_escolher_tipo_requerimento_url_resolves(self):
        url = reverse("escolher_tipo_requerimento", kwargs={'cpf': self.cliente.cpf})
        # Assumes the EscolherTipoRequerimentoView is used.
        self.assertEqual(resolve(url).func.view_class.__name__, "EscolherTipoRequerimentoView")
