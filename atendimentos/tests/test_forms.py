from django.test import TestCase
from django.utils import timezone
from atendimentos.forms import AtendimentoModelForm  # Assumindo que exista este form
from atendimentos.models import Atendimento
from clientes.models import Cliente

class TestAtendimentoForms(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            cpf="12345678901",
            nome="Fulano de Tal",
            data_nascimento="1980-01-01",
            telefone_whatsapp="11999998888",
            email="fulano@example.com"
        )

    def test_atendimento_form_valid(self):
        form_data = {
            "data": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cliente": self.cliente.cpf,
            "descricao": "Descrição de teste",
            "observacao": "Observação de teste"
        }
        form = AtendimentoModelForm(data=form_data)
        self.assertTrue(form.is_valid(), "O formulário deve ser válido com todos os dados corretos.")

    def test_atendimento_form_required_fields(self):
        # Enviar dados vazios para testar os campos obrigatórios
        form = AtendimentoModelForm(data={})
        self.assertFalse(form.is_valid(), "O formulário não deve ser válido sem os dados obrigatórios.")
        self.assertIn("data", form.errors, "O campo 'data' deve ser obrigatório.")
        self.assertIn("cliente", form.errors, "O campo 'cliente' deve ser obrigatório.")
        self.assertIn("descricao", form.errors, "O campo 'descricao' deve ser obrigatório.")
