from django.test import TestCase
import uuid
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from clientes.models import Cliente
from requerimentos.models import (
    EstadoExigencia,
    HistoricoMudancaEstadoRequerimentoRecurso,
    Natureza,
    Servico,
    RequerimentoInicial,
    RequerimentoRecurso,
    EstadoRequerimentoInicial,
    EstadoRequerimentoRecurso,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
    HistoricoMudancaEstadoRequerimentoInicial,
)
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission


def generate_unique_cpf():
    return str(uuid.uuid4().int)[:11]


def generate_unique_protocolo():
    return str(uuid.uuid4().int)[:15]


class TestRequerimentoViews(TestCase):
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

        # Create a Servico instance (objeto de referência que não muda)
        cls.servico = Servico.objects.create(
            nome="Aposentadoria por Idade Urbana"
        )

        # Create Estado objects for requerimentos (objetos de referência)
        cls.estado_inicial = EstadoRequerimentoInicial.objects.create(nome="em análise")
        cls.estado_recurso = EstadoRequerimentoRecurso.objects.create(nome="em análise na junta")

        # Objects for exigencias (objetos de configuração que não mudam)
        cls.natureza = Natureza.objects.create(nome="Documentacao")
        cls.estado_exigencia = EstadoExigencia.objects.create(nome="em análise")

    def setUp(self):
        # Login do usuário a cada teste
        self.client.force_login(self.user)

        # Create a Cliente instance for testing (precisa ser único a cada teste)
        self.cpf = generate_unique_cpf()
        self.cliente = Cliente.objects.create(
            cpf=self.cpf,
            nome="Teste Cliente",
            data_nascimento="1990-01-01",
            telefone_whatsapp="1234567890",
            email="teste@cliente.com",
        )

        # Create RequerimentoInicial and RequerimentoRecurso objects (dependem do cliente único)
        self.protocolo_inicial = generate_unique_protocolo()
        self.requerimento_inicial = RequerimentoInicial.objects.create(
            protocolo=self.protocolo_inicial,
            NB="NBINICIAL",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2021-01-01",
            estado=self.estado_inicial,
        )
        self.protocolo_recurso = generate_unique_protocolo()
        self.requerimento_recurso = RequerimentoRecurso.objects.create(
            protocolo=self.protocolo_recurso,
            NB="NBRECUSO",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2021-02-02",
            estado=self.estado_recurso,
        )

    def test_escolher_tipo_requerimento_get(self):
        url = reverse("escolher_tipo_requerimento", kwargs={"cpf": self.cliente.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_escolher_tipo_requerimento_post_initial(self):
        url = reverse("escolher_tipo_requerimento", kwargs={"cpf": self.cliente.cpf})
        response = self.client.post(url, {"tipo_requerimento": "inicial"})
        expected_url = reverse("adicionar_requerimento_inicial", kwargs={"cpf": self.cliente.cpf})
        self.assertRedirects(response, expected_url)

    def test_escolher_tipo_requerimento_post_recurso(self):
        url = reverse("escolher_tipo_requerimento", kwargs={"cpf": self.cliente.cpf})
        response = self.client.post(url, {"tipo_requerimento": "recurso"})
        expected_url = reverse("adicionar_requerimento_recurso", kwargs={"cpf": self.cliente.cpf})
        self.assertRedirects(response, expected_url)

    def test_requerimento_inicial_create_view_get(self):
        url = reverse("adicionar_requerimento_inicial", kwargs={"cpf": self.cliente.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_recurso_create_view_get(self):
        url = reverse("adicionar_requerimento_recurso", kwargs={"cpf": self.cliente.cpf})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_inicial_detail_view_get(self):
        url = reverse("requerimento_inicial", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_inicial.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_recurso_detail_view_get(self):
        url = reverse("requerimento_recurso", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_recurso.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_inicial_update_view_get(self):
        url = reverse("atualizar_requerimento_inicial", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_inicial.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_recurso_update_view_get(self):
        url = reverse("atualizar_requerimento_recurso", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_recurso.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_inicial_delete_view_get(self):
        url = reverse("excluir_requerimento_inicial", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_inicial.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_recurso_delete_view_get(self):
        url = reverse("excluir_requerimento_recurso", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_recurso.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_exigencia_requerimento_inicial_create_view_get(self):
        url = reverse("adicionar_exigencia_requerimento_inicial", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_inicial.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_exigencia_requerimento_recurso_create_view_get(self):
        url = reverse("adicionar_exigencia_requerimento_recurso", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_recurso.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_exigencia_requerimento_inicial_update_view_get(self):
        # Create an exigencia for each requerimento to test related views if necessary
        exigencia_inicial = ExigenciaRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            data="2021-01-10",
            natureza=self.natureza,  # Assumes a Natureza instance with id=1 exists or use a dummy integer if not used in view tests
            estado=self.estado_exigencia,    # Assumes EstadoExigencia instance with id=1 exists
        )

        url = reverse("atualizar_exigencia_requerimento_inicial", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_inicial.id,
            "exigencia_pk": exigencia_inicial.id,
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_exigencia_requerimento_recurso_update_view_get(self):
        # Create an exigencia for each requerimento to test related views if necessary
        exigencia_recurso = ExigenciaRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            data="2021-02-10",
            natureza=self.natureza,
            estado=self.estado_exigencia,
        )
        url = reverse("atualizar_exigencia_requerimento_recurso", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_recurso.id,
            "exigencia_pk": exigencia_recurso.id,
        })
        response = self.client.get(url)
        # print(response.context)
        self.assertEqual(response.status_code, 200)

    def test_exigencia_requerimento_inicial_delete_view_get(self):
        # Create an exigencia for each requerimento to test related views if necessary
        exigencia_inicial = ExigenciaRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            data="2021-01-10",
            natureza=self.natureza,  # Assumes a Natureza instance with id=1 exists or use a dummy integer if not used in view tests
            estado=self.estado_exigencia,    # Assumes EstadoExigencia instance with id=1 exists
        )
        url = reverse("excluir_exigencia_requerimento_inicial", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_inicial.id,
            "exigencia_pk": exigencia_inicial.id,
        })
        response = self.client.get(url)
        # print(response.context)
        self.assertEqual(response.status_code, 200)

    def test_exigencia_requerimento_recurso_delete_view_get(self):
        # Create an exigencia for each requerimento to test related views if necessary
        exigencia_recurso = ExigenciaRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            data="2021-02-10",
            natureza=self.natureza,
            estado=self.estado_exigencia,
        )
        url = reverse("excluir_exigencia_requerimento_recurso", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_recurso.id,
            "exigencia_pk": exigencia_recurso.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_inicial_ciencia_view_get(self):
        url = reverse("ciencia_requerimento_inicial", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_inicial.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_recurso_ciencia_view_get(self):
        url = reverse("ciencia_requerimento_recurso", kwargs={
            "cpf": self.cliente.cpf,
            "pk": self.requerimento_recurso.id
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mudanca_estado_requerimento_inicial_create_view_get(self):
        # Create EstadoExigencia instance
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Deferido")

        # Create HistoricoMudancaEstadoRequerimentoInicial instance
        HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.requerimento_inicial.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        self.assertEqual(self.requerimento_inicial.estado, estado_novo)

    def test_mudanca_estado_requerimento_inicial_create_indeferido_view_get(self):
        # Create EstadoExigencia instance
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Indeferido")

        # Create HistoricoMudancaEstadoRequerimentoInicial instance
        HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.requerimento_inicial.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        self.assertEqual(self.requerimento_inicial.estado, estado_novo)

    def test_mudanca_estado_requerimento_recurso_create_view_get(self):
        # Create EstadoExigencia instance
        estado_novo = EstadoRequerimentoRecurso.objects.create(nome="Concluído Deferido")

        # Create HistoricoMudancaEstadoRequerimentoRecurso instance
        HistoricoMudancaEstadoRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            estado_anterior=self.requerimento_recurso.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        self.assertEqual(self.requerimento_recurso.estado, estado_novo)

    def test_mudanca_estado_requerimento_inicial_delete_view_get(self):
        # Create a new Estado for the change
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Deferido")

        historico = HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.requerimento_inicial.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        # Use distinct keyword arguments for each id to avoid duplicate keys
        url = reverse(
            "excluir_mudanca_estado_requerimento_inicial",
            kwargs={
                "cpf": self.cliente.cpf,
                "pk": self.requerimento_inicial.id,
                "hist_pk": historico.id,
            }
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_mudanca_estado_requerimento_recurso_delete_view_get(self):
        # Create a new Estado for the change
        estado_novo = EstadoRequerimentoRecurso.objects.create(nome="Concluído Deferido")

        historico = HistoricoMudancaEstadoRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            estado_anterior=self.requerimento_recurso.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        # Use distinct keyword arguments for each id to avoid duplicate keys
        url = reverse(
            "excluir_mudanca_estado_requerimento_recurso",
            kwargs={
                "cpf": self.cliente.cpf,
                "pk": self.requerimento_recurso.id,
                "hist_pk": historico.id,
            }
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_requerimento_inicial_update_view_post(self):
        url = reverse("atualizar_requerimento_inicial", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_inicial.id})
        new_data = {
            # "protocolo": "PROTOINICIAL_UPDATED",  # Assuming this is not editable
            "NB": self.requerimento_inicial.NB,
            "servico": self.servico.id,
            "data": "2025-01-15",
            # Include required fields for the form; assuming other fields are optional or handled in the form.
        }
        response = self.client.post(url, new_data)
        # Expect a redirect after a successful update
        self.assertEqual(response.status_code, 302)

    def test_requerimento_recurso_update_view_post(self):
        url = reverse("atualizar_requerimento_recurso", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_recurso.id})
        new_data = {
            # "protocolo": "PROTORECUSO_UPDATED",  # Assuming this is not editable
            "NB": self.requerimento_recurso.NB,
            "servico": self.servico.id,
            "data": "2021-02-15",
        }
        response = self.client.post(url, new_data)
        self.assertEqual(response.status_code, 302)
