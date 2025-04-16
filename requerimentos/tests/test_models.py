from django.test import TransactionTestCase
import uuid
from django.utils import timezone
from clientes.models import Cliente

from requerimentos.models import (
    HistoricoMudancaEstadoRequerimentoRecurso,
    Servico,
    RequerimentoInicial,
    RequerimentoRecurso,
    EstadoRequerimentoInicial,
    EstadoRequerimentoRecurso,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
    EstadoExigencia,
    Natureza,
    HistoricoMudancaEstadoRequerimentoInicial,
)


def generate_unique_cpf():
    return str(uuid.uuid4().int)[:11]


def generate_unique_protocolo():
    return str(uuid.uuid4().int)[:15]


class TestModels(TransactionTestCase):
    def setUp(self):
        self.cpf = generate_unique_cpf()
        # Create a common Cliente instance
        self.cliente = Cliente.objects.create(
            cpf=self.cpf,
            nome="Teste Cliente",
            data_nascimento="1990-01-01",
            telefone_whatsapp="1234567890",
            email="teste@cliente.com",
        )
        # Create a Servico instance
        self.servico = Servico.objects.create(nome="Teste Servico")

        # Create Estado instances for requerimento inicial and recurso
        self.estado_inicial = EstadoRequerimentoInicial.objects.create(nome="em análise")
        estado_recurso_choice = [estado for estado in EstadoRequerimentoRecurso.ESTADOS_RECURSOS if estado[0] == "em análise na junta"]
        self.estado_recurso = None
        if estado_recurso_choice:
            self.estado_recurso = EstadoRequerimentoRecurso.objects.create(nome=estado_recurso_choice[0][0])

        # Create RequerimentoInicial instance
        self.protocolo_inicial = generate_unique_protocolo()
        self.requerimento_inicial = RequerimentoInicial.objects.create(
            protocolo=self.protocolo_inicial,
            NB="NB123",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2021-05-05",
            estado=self.estado_inicial,
        )
        # Create RequerimentoRecurso instance
        self.protocolo_recurso = generate_unique_protocolo()
        self.requerimento_recurso = RequerimentoRecurso.objects.create(
            protocolo=self.protocolo_recurso,
            NB="NB456",
            requerente_titular=self.cliente,
            servico=self.servico,
            data="2021-06-06",
            estado=self.estado_recurso,
        )
        # Create Natureza and EstadoExigencia instances
        self.natureza = Natureza.objects.create(nome="Documentacao")
        self.estado_exigencia = EstadoExigencia.objects.create(nome="em análise")

        # Create an ExigenciaRequerimentoInicial instance
        self.exigencia_inicial = ExigenciaRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            data="2021-05-10",
            natureza=self.natureza,
            estado=self.estado_exigencia,
        )
        # Create an ExigenciaRequerimentoRecurso instance
        self.exigencia_recurso = ExigenciaRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            data="2021-06-10",
            natureza=self.natureza,
            estado=self.estado_exigencia,
        )
        # Create updated EstadoRequerimentoInicial for historico change
        self.estado_inicial_updated = EstadoRequerimentoInicial.objects.create(nome="concluído deferido")
        self.estado_recurso_updated = EstadoRequerimentoRecurso.objects.create(nome="concluído deferido")

    def test_servico_str(self):
        self.assertEqual(str(self.servico), "Teste Servico")

    def test_requerimento_inicial_str(self):
        expected = (
            f"Requerimento de NB nº {self.requerimento_inicial.NB} para "
            f"{self.requerimento_inicial.servico.nome}: "
            f"{self.requerimento_inicial.requerente_titular.nome}, "
            f"{self.requerimento_inicial.requerente_titular.cpf}, "
            f"{self.requerimento_inicial.requerente_titular.data_nascimento}"
        )
        self.assertEqual(str(self.requerimento_inicial), expected)

    def test_requerimento_inicial_delete_method(self):
        # Soft delete the requerimento inicial
        self.requerimento_inicial.delete()
        self.requerimento_inicial.refresh_from_db()
        self.assertTrue(self.requerimento_inicial.is_deleted)

    def test_get_class_name_methods(self):
        self.assertEqual(self.requerimento_inicial.get_class_name(), "RequerimentoInicial")
        self.assertEqual(self.requerimento_recurso.get_class_name(), "RequerimentoRecurso")
        self.assertEqual(self.exigencia_inicial.get_class_name(), "ExigenciaRequerimentoInicial")
        self.assertEqual(self.exigencia_recurso.get_class_name(), "ExigenciaRequerimentoRecurso")

    def test_total_exigencias_requerimento_inicial_property(self):
        # Initially, there is one exigencia for requerimento_inicial
        self.assertEqual(self.requerimento_inicial.total_exigencias, 1)
        # Soft delete the exigencia and check that the count drops to zero
        self.exigencia_inicial.delete()
        self.assertEqual(self.requerimento_inicial.total_exigencias, 0)

    def test_total_mudancas_estado_requerimento_inicial_property(self):
        # Initially, there is no historico entry
        self.assertEqual(self.requerimento_inicial.total_mudancas_estado, 0)
        # Create another historico entry
        HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.estado_inicial_updated,
            estado_novo=self.estado_inicial,
            observacao="Reverter mudança",
            data_mudanca=timezone.now(),
        )
        self.assertEqual(self.requerimento_inicial.total_mudancas_estado, 1)

    def test_exigencia_requerimento_inicial_str(self):
        expected = (
            f"Exigência: id nº {self.exigencia_inicial.id} do NB nº "
            f"{self.exigencia_inicial.requerimento.NB} de "
            f"{self.exigencia_inicial.requerimento.requerente_titular.nome}, "
            f"{self.exigencia_inicial.requerimento.requerente_titular.cpf}"
        )
        self.assertEqual(str(self.exigencia_inicial), expected)

    def test_historico_requerimento_inicial_str(self):
        # Create HistoricoMudancaEstadoRequerimentoInicial instance
        historico = HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=self.requerimento_inicial,
            estado_anterior=self.estado_inicial,
            estado_novo=self.estado_inicial_updated,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        expected = (
            f"{self.requerimento_inicial.protocolo} do estado "
            f"{self.estado_inicial.nome} para {self.estado_inicial_updated.nome} em "
            f"{historico.data_mudanca}"
        )
        self.assertEqual(str(historico), expected)

    def test_requerimento_recurso_str(self):
        expected = (
            f"Requerimento de NB nº {self.requerimento_inicial.NB} para "
            f"{self.requerimento_inicial.servico.nome}: "
            f"{self.requerimento_inicial.requerente_titular.nome}, "
            f"{self.requerimento_inicial.requerente_titular.cpf}, "
            f"{self.requerimento_inicial.requerente_titular.data_nascimento}"
        )
        self.assertEqual(str(self.requerimento_inicial), expected)

    def test_requerimento_recurso_delete_method(self):
        # Soft delete the requerimento inicial
        self.requerimento_inicial.delete()
        self.requerimento_inicial.refresh_from_db()
        self.assertTrue(self.requerimento_inicial.is_deleted)

    def test_total_exigencias_requerimento_recurso_property(self):
        # Initially, there is one exigencia for requerimento_recurso
        self.assertEqual(self.requerimento_recurso.total_exigencias, 1)
        # Soft delete the exigencia and check that the count drops to zero
        self.exigencia_recurso.delete()
        self.assertEqual(self.requerimento_recurso.total_exigencias, 0)

    def test_total_mudancas_estado_requerimento_recurso_property(self):
        # Initially, there is no historico entry
        self.assertEqual(self.requerimento_recurso.total_mudancas_estado, 0)
        # Create another historico entry
        HistoricoMudancaEstadoRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            estado_anterior=self.estado_recurso_updated,
            estado_novo=self.estado_recurso,
            observacao="Reverter mudança",
            data_mudanca=timezone.now(),
        )
        self.assertEqual(self.requerimento_recurso.total_mudancas_estado, 1)

    def test_exigencia_requerimento_recurso_str(self):
        expected = (
            f"Exigência: id nº {self.exigencia_recurso.id} do NB nº "
            f"{self.exigencia_recurso.requerimento.NB} de "
            f"{self.exigencia_recurso.requerimento.requerente_titular.nome}, "
            f"{self.exigencia_recurso.requerimento.requerente_titular.cpf}"
        )
        self.assertEqual(str(self.exigencia_recurso), expected)

    def test_historico_requerimento_recurso_str(self):
        # Create HistoricoMudancaEstadoRequerimentoRecurso instance
        historico = HistoricoMudancaEstadoRequerimentoRecurso.objects.create(
            requerimento=self.requerimento_recurso,
            estado_anterior=self.estado_recurso,
            estado_novo=self.estado_recurso_updated,
            observacao="Teste mudança",
            data_mudanca=timezone.now(),
        )
        expected = (
            f"{self.requerimento_recurso.protocolo} do estado "
            f"{self.estado_recurso.nome} para {self.estado_recurso_updated.nome} em "
            f"{historico.data_mudanca}"
        )
        self.assertEqual(str(historico), expected)
