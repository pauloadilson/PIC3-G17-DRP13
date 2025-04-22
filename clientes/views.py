from datetime import datetime
from django.http import Http404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from agenda.models import Evento
from clientes.models import Cliente
from requerimentos.models import (
    RequerimentoInicial,
    RequerimentoRecurso,
    Requerimento,
)
from clientes.forms import ClienteModelForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from itertools import chain
from django.utils import timezone

from clientes.serializers import ClienteSerializer
from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Count
import plotly.express as px


class IndexView(TemplateView):
    template_name = "index.html"
    title = "Página inicial"

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super(IndexView, self).get_context_data(**kwargs)
        hoje = timezone.localdate()
        hoje_aware = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
        eventos = Evento.objects.filter(
            data_inicio__gte=hoje_aware,
        ).order_by('data_inicio')[:5]
        context["title"] = self.title
        context["agenda"] = eventos
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class ClientesListView(ListView):
    model = Cliente
    template_name = "clientes.html"
    context_object_name = "clientes"
    title = "Clientes"
    ordering = ["nome"]
    paginate_by = 10

    def get_queryset(self):
        clientes = super().get_queryset().filter(is_deleted=False)
        busca = self.request.GET.get("busca")
        if busca:
            clientes = clientes.filter(cpf__icontains=busca)
        return clientes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class ClienteCreateView(CreateView):
    model = Cliente
    template_name = "form.html"
    form_class = ClienteModelForm
    title = "Novo Cliente"

    def get_context_data(self, **kwargs):
        context = super(ClienteCreateView, self).get_context_data(**kwargs)
        # adicionar o título da página e o título do formulário ao contexto
        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy("cliente", kwargs={"cpf": self.object.cpf})


@method_decorator(login_required(login_url="login"), name="dispatch")
class ClienteDetailView(DetailView):
    model = Cliente
    template_name = "cliente.html"
    context_object_name = "cliente"
    slug_field = "cpf"
    slug_url_kwarg = "cpf"

    def get_object(self, queryset=None):
        cpf = self.kwargs.get('cpf')
        obj = get_object_or_404(Cliente, cpf=cpf)
        if obj.is_deleted:
            raise Http404("Cliente não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(ClienteDetailView, self).get_context_data(**kwargs)
        cliente_id = self.object.cpf
        title = f"Cliente {cliente_id}"
        requerimentos_iniciais = RequerimentoInicial.objects.filter(
            is_deleted=False
        ).filter(requerente_titular__cpf__icontains=cliente_id)
        recursos = RequerimentoRecurso.objects.filter(is_deleted=False).filter(
            requerente_titular__cpf__icontains=cliente_id
        )
        atendimentos_cliente = self.object.cliente_atendimento.filter(
            is_deleted=False
        )
        qtde_instancias_filhas = self.object.total_requerimentos + self.object.total_atendimentos

        context["title"] = title
        context["requerimentos"] = requerimentos_iniciais
        context["recursos"] = recursos
        context["atendimentos"] = atendimentos_cliente
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class ClienteUpdateView(UpdateView):
    model = Cliente
    template_name = "form.html"
    form_class = ClienteModelForm
    title = "Editando Cliente"
    form_title_identificador = None
    slug_field = "cpf"
    slug_url_kwarg = "cpf"

    def get_success_url(self):
        return reverse_lazy("cliente", kwargs={"cpf": self.object.cpf})

    def get_context_data(self, **kwargs):
        context = super(ClienteUpdateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f"CPF nº {self.object.cpf}"
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Cliente não encontrado")
        return obj


@method_decorator(login_required(login_url="login"), name="dispatch")
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "delete.html"
    success_url = "/clientes/"
    title = "Excluindo Cliente"
    tipo_objeto = "o cliente"
    slug_field = "cpf"
    slug_url_kwarg = "cpf"

    def get_context_data(self, **kwargs):
        context = super(ClienteDeleteView, self).get_context_data(**kwargs)

        cliente_id = self.object.cpf
        requerimentos_cliente = RequerimentoInicial.objects.filter(
            is_deleted=False
        ).filter(requerente_titular__cpf__icontains=cliente_id)
        recursos_cliente = RequerimentoRecurso.objects.filter(is_deleted=False).filter(
            requerente_titular__cpf__icontains=cliente_id
        )
        result_list = list(chain(requerimentos_cliente, recursos_cliente))
        qtde_instancias_filhas = self.object.total_requerimentos

        context["title"] = self.title
        context["form_title_identificador"] = f"de CPF nº {self.object.cpf}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        context["result_list"] = result_list
        print(result_list)
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Cliente não encontrado")
        return obj


class ClienteCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_queryset(self):
        return Cliente.objects.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save()


class ClienteRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

    def get_object(self):
        return get_object_or_404(Cliente, cpf=self.kwargs['cpf'])

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


@method_decorator(login_required(login_url="login"), name="dispatch")
class DashboardView(TemplateView):
    template_name = "dashboard.html"
    title = "Painel de Análise"

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super(DashboardView, self).get_context_data(**kwargs)

        ano_atual = datetime.now().year

        # Gráfico de número de requerimentos abertos no ano
        requerimentos_por_mes = Requerimento.objects.filter(is_deleted=False).filter(data__year=ano_atual).annotate(mes=ExtractMonth('data')).values('mes').annotate(total=Count('id')).order_by('mes')
        meses = [r['mes'] for r in requerimentos_por_mes]
        totais_meses = [r['total'] for r in requerimentos_por_mes]

        fig = px.bar(x=meses, y=totais_meses, labels={'x': 'Mês', 'y': 'Número de Requerimentos'}, title=f'Número de Requerimentos Abertos em {ano_atual}')
        fig.update_xaxes(tickvals=meses)
        fig.update_layout(width=500, height=400)
        chart = fig.to_html()
        context['grafico1'] = chart

        # Gráfico de número de atendimentos realizados no ano
        requerimentos_por_ano = Requerimento.objects.filter(is_deleted=False).annotate(ano=ExtractYear('data')).values('ano').annotate(total=Count('id')).order_by('ano')
        anos = [r['ano'] for r in requerimentos_por_ano]
        totais_anos = [r['total'] for r in requerimentos_por_ano]

        fig = px.bar(x=anos, y=totais_anos, labels={'x': 'Ano', 'y': 'Número de Requerimentos por ano'}, title='Número de Requerimentos Abertos por Ano')
        fig.update_xaxes(tickvals=anos)
        fig.update_layout(width=500, height=400)
        chart2 = fig.to_html()
        context['grafico2'] = chart2

        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy("atendimentos")
