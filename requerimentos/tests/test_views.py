from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from clientes.models import Cliente

from requerimentos.models import (
    EstadoExigencia,
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
  
class TestRequerimentoViews(TestCase):
    def setUp(self):
        # Create and login a dummy user
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_login(self.user)
  
        # Create a Cliente instance for testing
        self.cliente = Cliente.objects.create(
            cpf="11122233344",
            nome="Teste Cliente",
            data_nascimento="1990-01-01",
            telefone_whatsapp="1234567890",
            email="teste@cliente.com",
        )
  
        # Create a Servico instance
        self.servico = Servico.objects.create(
            nome="Aposentadoria por Idade Urbana"
        )
  
        # Create Estado objects for requerimentos
        self.estado_inicial = EstadoRequerimentoInicial.objects.create(nome="em análise")
        self.estado_recurso = EstadoRequerimentoRecurso.objects.create(nome="em análise na junta")
  
        # Create RequerimentoInicial and RequerimentoRecurso objects for detail/update/delete views
        self.requerimento_inicial = RequerimentoInicial.objects.create(
            protocolo="PROTOINICIAL",
            NB="NBINICIAL",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2021-01-01",
            estado=self.estado_inicial,
        )
        self.requerimento_recurso = RequerimentoRecurso.objects.create(
            protocolo="PROTORECUSO",
            NB="NBRECUSO",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2021-02-02",
            estado=self.estado_recurso,
        )
        
        # Objects for exigencias
        self.natureza = Natureza.objects.create(nome="Documentacao")
        self.estado_exigencia = EstadoExigencia.objects.create(nome="em análise")


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
  
    def test_mudanca_estado_requerimento_inicial_create_view_get(self):
        # Create EstadoExigencia instance
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Deferido")
  
        # Create HistoricoMudancaEstadoRequerimentoInicial instance
        historico = HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.requerimento_inicial.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        self.assertEqual(self.requerimento_inicial.estado, estado_novo)
                       
    def test_mudanca_estado_requerimento_inicial_delete_view_get(self):
        # Create a new Estado for the change
        estado_novo = EstadoRequerimentoInicial.objects.create(nome="Concluído Deferido")
        
        requerimento_inicial = RequerimentoInicial.objects.create(
            protocolo="PROTOINICIALMUDANCA",
            NB="NBINICIALMUDANCA",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2025-01-01",
            estado=self.estado_inicial,
        )
        
        historico = HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=requerimento_inicial,
            estado_anterior=requerimento_inicial.estado,
            estado_novo=estado_novo,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        # Use distinct keyword arguments for each id to avoid duplicate keys
        url = reverse(
            "excluir_mudanca_estado_requerimento_inicial",
            kwargs={
                "cpf": self.cliente.cpf,
                "pk": requerimento_inicial.id,
                "hist_pk": historico.id,
            }
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # Additional tests

    def test_requerimento_inicial_update_view_post(self):
        url = reverse("atualizar_requerimento_inicial", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_inicial.id})
        new_data = {
            "protocolo": "PROTOINICIAL_UPDATED",
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
            "protocolo": "PROTORECUSO_UPDATED",
            "NB": self.requerimento_recurso.NB,
            "servico": self.servico.id,
            "data": "2021-02-15",
        }
        response = self.client.post(url, new_data)
        self.assertEqual(response.status_code, 302)

    # def test_exigencia_requerimento_inicial_create_view_post(self):
    #     url = reverse("adicionar_exigencia_requerimento_inicial", kwargs={
    #         "cpf": self.cliente.cpf, 
    #         "pk": self.requerimento_inicial.id
    #     })
    #     new_data = {
    #         "data": "2021-01-20",
    #         "natureza": self.natureza.id,
    #         "estado": self.estado_exigencia.id,
    #     }
    #     response = self.client.post(url, new_data)
    #     print(response.context)
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse("requerimento_inicial", kwargs={
    #         "cpf": self.cliente.cpf, 
    #         "pk": self.requerimento_inicial.id
    #     }))
    #     self.assertTrue(ExigenciaRequerimentoInicial.objects.filter(data="2021-01-20").exists())
        

    # def test_exigencia_requerimento_recurso_create_view_post(self):
    #     url = reverse("adicionar_exigencia_requerimento_recurso", kwargs={"cpf": self.cliente.cpf, "pk": self.requerimento_recurso.id})
    #     new_data = {
    #         "data": "2021-02-20",
    #         "natureza": self.natureza.id,
    #         "estado": self.estado_exigencia.id,
    #     }
    #     response = self.client.post(url, new_data)
    #     self.assertEqual(response.status_code, 302)