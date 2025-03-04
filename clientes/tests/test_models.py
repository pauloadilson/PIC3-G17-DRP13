from django.test import TestCase
from clientes.models import Cliente
from requerimentos.models import EstadoRequerimentoInicial, RequerimentoInicial, Servico

from django.urls import reverse

# Create your tests here.
class TestModels(TestCase):
    def setUp(self):
        self.cliente1 = Cliente.objects.create(
            cpf="12345678901",
            nome="Fulano de Tal",
            data_nascimento="1981-01-21",
            telefone="18991234567",
            observacao_telefone="Recado com Júlio (vizinho)",
            telefone_whatsapp="18991234567",
            email="pauloadilson@gmail.com"
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

    def test_cliente_model(self):
        self.assertEqual(self.cliente1.cpf, "12345678901")
        self.assertEqual(self.cliente1.nome, "Fulano de Tal")
        self.assertEqual(self.cliente1.data_nascimento, "1981-01-21")
        self.assertEqual(self.cliente1.telefone, "18991234567")
        self.assertEqual(self.cliente1.observacao_telefone, "Recado com Júlio (vizinho)")
        self.assertEqual(self.cliente1.telefone_whatsapp, "18991234567")
        self.assertEqual(self.cliente1.email, "pauloadilson@gmail.com")
        self.assertEqual(self.cliente1.is_deleted, False)
        self.assertEqual(str(self.cliente1), "12345678901, Fulano de Tal, 1981-01-21, 18991234567, 18991234567, pauloadilson@gmail.com")
        self.assertEqual(self.cliente1.get_class_name(), "Cliente")
        self.assertEqual(self.cliente1.total_requerimentos, 1)
        self.requerimento_inicial1.delete()
        self.cliente1.delete()
        self.assertEqual(self.cliente1.is_deleted, True)

