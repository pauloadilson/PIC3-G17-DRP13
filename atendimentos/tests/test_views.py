from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone
from django.contrib.auth.models import User
from clientes.models import Cliente
from atendimentos.models import Atendimento

class TestAtendimentoViews(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.user.set_password("secretkey")
        self.user.save()
        self.client.login(username="testuser", password="secretkey")
        
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

    def test_atendimentos_list_view_GET(self):
        url = reverse("atendimentos")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "atendimentos.html")
        self.assertEqual(response.context.get("title"), "Atendimentos")

    def test_atendimento_create_view_GET(self):
        url = reverse("adicionar_atendimento")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form.html")
        self.assertEqual(response.context.get("title"), "Novo Atendimento")
        
    def test_atendimento_cliente_create_view_GET(self):
        url = reverse("adicionar_atendimento_cliente", kwargs={"cpf": self.cliente.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form.html")
        self.assertEqual(response.context.get("title"), "Novo Atendimento")

    def test_atendimento_detail_view_GET(self):
        url = reverse("atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "atendimento.html")
        self.assertEqual(response.context.get("title"), "Atendimento")
        self.assertEqual(response.context.get("cliente").cpf, self.cliente.cpf)

    def test_atendimento_update_view_GET(self):
        url = reverse("atualizar_atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form.html")
        self.assertEqual(response.context.get("title"), "Editando Atendimento")

    def test_atendimento_delete_view_GET(self):
        url = reverse("excluir_atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete.html")
        self.assertEqual(response.context.get("title"), "Excluindo Atendimento")
        
    def test_atendimento_create_view_POST(self):
        url = reverse("adicionar_atendimento_cliente", kwargs={"cpf": self.cliente.cpf})
        data = {
            "data": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cliente": self.cliente.cpf,
            "descricao": "Teste de criação via POST",
            "observacao": "Observação via POST"
        }
        response = self.client.post(url, data)
        # A criação bem-sucedida deve redirecionar para a lista de atendimentos
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("atendimentos"))
        self.assertTrue(Atendimento.objects.filter(descricao="Teste de criação via POST").exists())

    def test_atendimento_update_view_POST(self):
        url = reverse("atualizar_atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        new_description = "Teste de update via POST"
        new_observacao = "Atualização via POST"
        data = {
            "data": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cliente": self.cliente.cpf,
            "descricao": new_description,
            "observacao": new_observacao
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("atendimentos"))
        self.atendimento.refresh_from_db()
        self.assertEqual(self.atendimento.descricao, new_description)
        self.assertEqual(self.atendimento.observacao, new_observacao)

    def test_atendimento_delete_view_DELETE(self):
        url = reverse("excluir_atendimento", kwargs={"cpf": self.cliente.cpf, "pk": self.atendimento.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("atendimentos"))
        with self.assertRaises(Atendimento.DoesNotExist):
            Atendimento.objects.get(pk=self.atendimento.id)

