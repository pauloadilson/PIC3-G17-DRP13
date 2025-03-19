from django.test import TransactionTestCase
import uuid
from django.urls import reverse, resolve
from django.utils import timezone
from django.contrib.auth.models import User
from clientes.models import Cliente
from atendimentos.models import Atendimento
from atendimentos.views import (
    AtendimentosListView,
    AtendimentoCreateView,
    AtendimentoDetailView,
    AtendimentoUpdateView,
    AtendimentoDeleteView,
)

def generate_unique_cpf():
    return str(uuid.uuid4().int)[:11]

class TestAtendimentoUrls(TransactionTestCase):
    def setUp(self):
        self.cpf = generate_unique_cpf()
        self.cliente = Cliente.objects.create(
            cpf=self.cpf,
            nome="Fulano de Tal",
            data_nascimento="1981-01-21",
            telefone_whatsapp="18991234567",
            email="fulano@example.com"
        )
        self.atendimento = Atendimento.objects.create(
            data=timezone.now(),
            cliente=self.cliente,
            descricao="Teste de atendimento URL",
            observacao="Teste observação"
        )

    def test_atendimentos_list_url_resolves(self):
        url = reverse("atendimentos")
        self.assertEqual(resolve(url).func.view_class, AtendimentosListView)

    def test_atendimento_create_url_resolves(self):
        url = reverse("adicionar_atendimento")
        self.assertEqual(resolve(url).func.view_class, AtendimentoCreateView)

    def test_atendimento_detail_url_resolves(self):
        url = reverse("atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        self.assertEqual(resolve(url).func.view_class, AtendimentoDetailView)

    def test_atendimento_update_url_resolves(self):
        url = reverse("atualizar_atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        self.assertEqual(resolve(url).func.view_class, AtendimentoUpdateView)

    def test_atendimento_delete_url_resolves(self):
        url = reverse("excluir_atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        self.assertEqual(resolve(url).func.view_class, AtendimentoDeleteView)
        