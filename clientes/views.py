from datetime import datetime
from django.http import Http404
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
from cpprev.permissions import GlobalDefaultPermission
from requerimentos.models import (
    RequerimentoInicial,
    RequerimentoRecurso,
)
from clientes.forms import ClienteModelForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from itertools import chain
from django.utils import timezone

from rest_framework import viewsets
from clientes.serializers import (
    ClienteRetrieveSerializer,
    ClienteSerializer
)


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
    permission_required = "clientes.create_cliente"

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


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    queryset = Cliente.objects.filter(is_deleted=False)
    serializer_class = ClienteSerializer
    lookup_field = 'cpf'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteRetrieveSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'cliente_atendimento',
                'cliente_titular_requerimento'
            )
        return queryset
