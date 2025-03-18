from django.test import TestCase
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
class TestUrls(TestCase):
    def setUp(self) -> None:
        # Common objects
        self.cliente1 = Cliente.objects.create(
            cpf="12345678901",
            nome="Fulano de Tal",
            data_nascimento="1981-01-21",
            telefone_whatsapp="18991234567",
            email="paulo@paulo.com",
        )
        self.servico1 = Servico.objects.create(
            nome="Aposentadoria por Idade Urbana"
        )
        self.estado1 = EstadoRequerimentoInicial.objects.create(
            nome="em análise"
        )
        self.requerimento_inicial1 = RequerimentoInicial.objects.create(
            requerente_titular=self.cliente1,
            protocolo="123456123456123456",
            NB="456123456123456123",
            servico=self.servico1,
            data="2021-01-01",
            estado=self.estado1,
        )
        # Objects for requerimento_recurso
        self.estado_recurso = EstadoRequerimentoRecurso.objects.create(
            nome="em análise na junta"
        )
        self.requerimento_recurso1 = RequerimentoRecurso.objects.create(
            requerente_titular=self.cliente1,
            protocolo="987654321098765432",
            NB="321098765432109876",
            servico=self.servico1,
            data="2021-02-01",
            estado=self.estado_recurso,
        )
        self.natureza = Natureza.objects.create(nome="Documentação")
        
        self.estado_exigencia = EstadoExigencia.objects.create(nome="em análise")
        
        self.exigencia_inicial = ExigenciaRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial1,
            natureza=self.natureza,
            estado=self.estado_exigencia,
            descricao="Falta documento X",
            prazo=timezone.now(),
        )
        self.exigencia_recurso = ExigenciaRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso1,
            natureza=self.natureza,
            estado=self.estado_exigencia,
            descricao="Falta documento Y",
            prazo=timezone.now(),
        )

    def test_adicionar_requerimento_inicial_url_resolves(self):
        url = reverse("adicionar_requerimento_inicial", kwargs={'cpf': self.cliente1.cpf})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialCreateView")
    
    def test_requerimento_detail_url_resolves(self):
        url = reverse("requerimento_inicial", kwargs={'cpf': self.cliente1.cpf, 'pk': self.requerimento_inicial1.id})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialDetailView")

    def test_adicionar_exigencia_requerimento_inicial_url_resolves(self):
        url = reverse("adicionar_exigencia_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialCreateView")
        
    def test_atualizar_requerimento_inicial_url_resolves(self):
        url = reverse("atualizar_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialUpdateView")

    def test_excluir_requerimento_inicial_url_resolves(self):
        url = reverse("excluir_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialDeleteView")

    def test_ciencia_requerimento_inicial_url_resolves(self):
        url = reverse("ciencia_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "MudancaEstadoRequerimentoInicialCreateView")

    def test_excluir_mudanca_estado_requerimento_inicial_url_resolves(self):
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Deferido")
        
        historico = HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial1,
            estado_anterior=self.requerimento_inicial1.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        url = reverse("excluir_mudanca_estado_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id,
            "hist_pk": historico.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "MudancaEstadoRequerimentoInicialDeleteView")

    def test_adicionar_requerimento_recurso_url_resolves(self):
        url = reverse("adicionar_requerimento_recurso", kwargs={'cpf': self.cliente1.cpf})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoCreateView")

    def test_requerimento_recurso_detail_url_resolves(self):
        url = reverse("requerimento_recurso", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_recurso1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoDetailView")

    def test_atualizar_requerimento_recurso_url_resolves(self):
        url = reverse("atualizar_requerimento_recurso", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_recurso1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoUpdateView")

    def test_excluir_requerimento_recurso_url_resolves(self):
        url = reverse("excluir_requerimento_recurso", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_recurso1.id
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoRecursoDeleteView")

    def test_atualizar_exigencia_requerimento_inicial_url_resolves(self):
        url = reverse("atualizar_exigencia_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id,
            'pk_exigencia': self.exigencia_inicial.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialUpdateView")

    def test_excluir_exigencia_requerimento_inicial_url_resolves(self):
        url = reverse("excluir_exigencia_requerimento_inicial", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_inicial1.id,
            'pk_exigencia': self.exigencia_inicial.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialDeleteView")

    def test_adicionar_exigencia_requerimento_recurso_url_resolves(self):
        url = reverse("adicionar_exigencia_requerimento_recurso", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_recurso1.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoRecursoCreateView")

    def test_atualizar_exigencia_requerimento_recurso_url_resolves(self):
        url = reverse("atualizar_exigencia_requerimento_recurso", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_recurso1.id,
            'pk_exigencia': self.exigencia_recurso.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoRecursoUpdateView")

    def test_excluir_exigencia_requerimento_recurso_url_resolves(self):
        url = reverse("excluir_exigencia_requerimento_recurso", kwargs={
            'cpf': self.cliente1.cpf,
            'pk': self.requerimento_recurso1.id,
            'pk_exigencia': self.exigencia_recurso.id,
        })
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoRecursoDeleteView")

    def test_escolher_tipo_requerimento_url_resolves(self):
        url = reverse("escolher_tipo_requerimento", kwargs={'cpf': self.cliente1.cpf})
        # Assumes the EscolherTipoRequerimentoView is used.
        self.assertEqual(resolve(url).func.view_class.__name__, "EscolherTipoRequerimentoView")