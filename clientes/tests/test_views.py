from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from clientes.models import Cliente

class TestViews(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Roda apenas uma vez por classe de teste
        cls.user = User.objects.create_user(username='testuser', password='secretkey')
        content_type = ContentType.objects.get_for_model(Cliente)
        permission = Permission.objects.get(
            codename='add_cliente',
            content_type=content_type,
        )
        cls.user.user_permissions.add(permission)

        # URLs podem ser atributos de classe
        cls.index_url = reverse("index")
        cls.clientes_url = reverse("clientes")
        cls.adicionar_cliente_url = reverse("adicionar_cliente")

    def setUp(self):
        # Roda antes de cada teste
        # Assign the permission to the user
        self.client.login(username='testuser', password='secretkey')

    def test_index_GET(self):
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertEqual(response.context_data["title"], "Página inicial")
        self.assertContains(response, "Página inicial")

    def test_ClientesListView_GET(self):
        response = self.client.get(self.clientes_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "clientes.html")
        self.assertEqual(response.context_data["title"], "Clientes")

    def test_ClienteCreateView_GET(self):
        response = self.client.get(self.adicionar_cliente_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form.html")
        self.assertEqual(response.context_data["title"], "Novo Cliente")

    def test_ClienteCreateView_POST(self):
        response = self.client.post(self.adicionar_cliente_url, {
            "cpf": "12345678901",
            "nome": "Fulano de Tal",
            "data_nascimento": "1981-01-21",
            "telefone": "18991234567",
            "observacao_telefone": "Recado com Júlio (vizinho)",
            "telefone_whatsapp": "18991234567",
            "email": "pauloadilson@gmail.com",
        })

        # First, check for the 302 redirect
        if response.status_code != 302:
            print(f"Response content: {response.content}")
            print(f"Response status code: {response.status_code}")


        self.assertEqual(response.status_code, 302)

        # Now, follow the redirect
        follow_response = self.client.get(response.url)

        # Check that the redirect leads to the correct page
        self.assertEqual(follow_response.status_code, 200)

        # Now check the response contains the expected data (if applicable on the redirected page)
        self.assertTemplateUsed(follow_response, "cliente.html")
