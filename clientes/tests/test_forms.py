from django.test import TestCase
from clientes.forms import ClienteModelForm
import datetime


class TestForms(TestCase):
    def setUp(self):
        self.cliente_form_data = {
            'cpf': '12345678901',
            'nome': 'Fulano de Tal',
            'data_nascimento': '1981-01-21',
            'telefone_whatsapp': '18991234567',
            'email': 'paulo@paulo.com'
        }
        self.date_obj = datetime.datetime.strptime(self.cliente_form_data['data_nascimento'], '%Y-%m-%d').date()

    def test_cliente_form(self):
        form = ClienteModelForm(data=self.cliente_form_data)
        self.assertTrue(form.is_valid())
        cliente = form.save()
        self.assertEqual(cliente.cpf, '12345678901')
        self.assertEqual(cliente.nome, 'Fulano de Tal')
        self.assertEqual(cliente.data_nascimento, self.date_obj)
        self.assertEqual(cliente.telefone_whatsapp, '18991234567')
        self.assertEqual(cliente.email, 'paulo@paulo.com')
        self.assertEqual(cliente.is_deleted, False)
        cliente.delete()
        self.assertEqual(cliente.is_deleted, True)
