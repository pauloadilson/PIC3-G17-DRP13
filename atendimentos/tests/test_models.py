from django.test import TestCase
from django.utils import timezone
from clientes.models import Cliente
from atendimentos.models import Atendimento


class TestAtendimentoModel(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            cpf="12345678901",
            nome="Fulano de Tal",
            data_nascimento="1981-01-21",
            telefone_whatsapp="18991234567",
            email="fulano@example.com"
        )
        self.atendimento = Atendimento.objects.create(
            data=timezone.now(),
            cliente=self.cliente,
            descricao="Teste de atendimento",
            observacao="Nenhuma observação"
        )

    def test_str_method(self):
        esperado = f'Atendimento: id nº {self.atendimento.id} de {self.cliente.nome}, {self.cliente.cpf}'
        self.assertEqual(str(self.atendimento), esperado)
