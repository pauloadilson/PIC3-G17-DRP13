from django.test import TestCase
from django.urls import reverse, resolve

from clientes.models import Cliente
from requerimentos.models import EstadoRequerimentoInicial, RequerimentoInicial, Servico

class TestUrls(TestCase):
    def setUp(self) -> None:
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
            estado= self.estado1,
        )

    def test_adicionar_requerimento_inicial_url_resolves(self):
        url = reverse("adicionar_requerimento_inicial", kwargs={'cpf': self.cliente1.cpf})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialCreateView")
   
    def test_requerimento_detail_url_resolves(self):
        url = reverse("requerimento_inicial", kwargs={'cpf': self.cliente1.cpf, 'pk': self.requerimento_inicial1.id})
        self.assertEqual(resolve(url).func.view_class.__name__, "RequerimentoInicialDetailView")

    def test_adicionar_exigencia_requerimento_inicial_url_resolves(self):
        url = reverse("adicionar_exigencia_requerimento_inicial", kwargs={'cpf': self.cliente1.cpf, 'pk': self.requerimento_inicial1.id})
        self.assertEqual(resolve(url).func.view_class.__name__, "ExigenciaRequerimentoInicialCreateView")
        