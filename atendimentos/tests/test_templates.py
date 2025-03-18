from django.test import TestCase
from django.template.loader import get_template
from django.utils import timezone

class TestAtendimentosTemplate(TestCase):
  def setUp(self):
    # Create dummy cliente with attributes cpf and nome.
    self.cliente = type("DummyCliente", (), {"cpf": "12345678901", "nome": "Fulano de Tal"})
    # Create dummy requerimento with attribute NB.
    self.requerimento = type("DummyRequerimento", (), {"NB": "REQ123"})()
    # Create dummy atendimento with attributes data, cliente, requerimento, and id.
    self.atendimento = type(
      "DummyAtendimento", (), {
        "data": timezone.now(),
        "cliente": self.cliente,
        "requerimento": self.requerimento,
        "id": 1
      }
    )()
    self.atendimentos = [self.atendimento]

  def test_atendimentos_template_renders_content(self):
    template = get_template("atendimentos.html")
    context = {"atendimentos": self.atendimentos}
    rendered = template.render(context)
    # Verify title and button
    self.assertIn("Atendimentos", rendered)
    self.assertIn("Novo Atendimento", rendered)
    # Verify table headers
    self.assertIn("<th>Data</th>", rendered)
    self.assertIn("<th>Cliente</th>", rendered)
    self.assertIn("<th>Requerimento</th>", rendered)
    self.assertIn("Ações", rendered)
    # Check if atendimento values are rendered in UTC-3
    formatted_date = timezone.localtime(self.atendimento.data, timezone.get_fixed_timezone(-180)).strftime("%d/%m/%Y")
    self.assertIn(formatted_date, rendered)
    self.assertIn(self.cliente.nome, rendered)
    self.assertIn(self.requerimento.NB, rendered)