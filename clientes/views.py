from datetime import datetime
from itertools import chain

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from atendimentos.models import Atendimento
from agenda.models import Evento
from clientes.forms import ClienteModelForm
from cpprev.mixins import SoftDeleteGetMixin
from clientes.models import Cliente
from clientes.serializers import (
    ClienteRetrieveSerializer,
    ClienteSerializer
)
from cpprev.permissions import GlobalDefaultPermission
from requerimentos.models import (
    Requerimento,
    RequerimentoInicial,
    RequerimentoRecurso,
)


class IndexView(TemplateView):
    template_name = "index.html"
    title = "Página inicial"

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        hoje = timezone.localdate()
        hoje_aware = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
        eventos = Evento.objects.filter(
            data_inicio__gte=hoje_aware,
        ).order_by('data_inicio')[:5]
        context["title"] = self.title
        context["agenda"] = eventos
        return context


class ClientesListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes.html"
    context_object_name = "clientes"
    title = "Clientes"
    paginate_by = 10

    def get_ordering(self):
        """Retorna a ordenação da requisição ou o padrão."""
        return self.request.GET.get('ordering', 'nome,cpf')

    def get_queryset(self):
        busca = self.request.GET.get("busca")
        ordering_params = self.get_ordering()
        ordering = ordering_params.split(',')

        queryset = self.model.objects.filter(is_deleted=False)

        if busca:
            print(f"--- BUSCANDO CLIENTES COM CPF CONTENDO: {busca} ---")
            return queryset.filter(cpf__icontains=busca).order_by(*ordering)

        # Usa um número de versão para invalidar o cache de forma mais robusta
        version = cache.get_or_set('clientes_list_version_html', 1)
        cache_key = f"lista_de_clientes_{ordering_params}_v{version}"

        cached_queryset = cache.get(cache_key)
        if cached_queryset is None:
            print(f"--- CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
            cached_queryset = queryset.order_by(*ordering)
            cache.set(cache_key, cached_queryset, 900)  # 15 minutos
        else:
            print(f"+++ CACHE HIT ({cache_key}) +++ Servindo a lista do Redis!")

        return cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["current_ordering"] = self.get_ordering()
        return context


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    template_name = "form.html"
    form_class = ClienteModelForm
    title = "Novo Cliente"
    permission_required = "clientes.add_cliente"  # Permissão padrão do Django

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy("cliente", kwargs={"cpf": self.object.cpf})


class ClienteDetailView(LoginRequiredMixin, SoftDeleteGetMixin, DetailView):
    model = Cliente
    template_name = "cliente.html"
    context_object_name = "cliente"
    slug_field = "cpf"
    slug_url_kwarg = "cpf"

    def get_queryset(self):
        # Otimiza as consultas, buscando tudo de uma vez com prefetch_related
        return (
            super()
            .get_queryset()
            .prefetch_related(
                Prefetch(
                    "cliente_titular_requerimento",
                    queryset=Requerimento.objects.filter(is_deleted=False),
                    to_attr="requerimentos_ativos",
                ),
                Prefetch(
                    "cliente_atendimento",
                    queryset=Atendimento.objects.filter(is_deleted=False),
                    to_attr="atendimentos_ativos",
                ),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object

        # Os dados já foram pré-buscados, então não há novas queries aqui
        requerimentos = cliente.requerimentos_ativos
        atendimentos = cliente.atendimentos_ativos

        context["title"] = f"Cliente {cliente.nome}"
        context["requerimentos"] = [req for req in requerimentos if isinstance(req, RequerimentoInicial)]
        context["recursos"] = [req for req in requerimentos if isinstance(req, RequerimentoRecurso)]
        context["atendimentos"] = atendimentos
        context["qtde_instancias_filhas"] = len(requerimentos) + len(atendimentos)
        return context


class ClienteUpdateView(LoginRequiredMixin, SoftDeleteGetMixin, UpdateView):
    model = Cliente
    template_name = "form.html"
    form_class = ClienteModelForm
    title = "Editando Cliente"
    slug_field = "cpf"
    slug_url_kwarg = "cpf"

    def get_success_url(self):
        return reverse_lazy("cliente", kwargs={"cpf": self.object.cpf})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f"CPF nº {self.object.cpf}"
        return context


class ClienteDeleteView(LoginRequiredMixin, SoftDeleteGetMixin, DeleteView):
    model = Cliente
    template_name = "delete.html"
    success_url = reverse_lazy("clientes")
    title = "Excluindo Cliente"
    tipo_objeto = "o cliente"
    slug_field = "cpf"
    slug_url_kwarg = "cpf"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.object

        # Reutiliza a consulta otimizada para mostrar dependências
        requerimentos_cliente = Requerimento.objects.filter(
            is_deleted=False, requerente_titular=cliente
        )
        atendimentos_cliente = Atendimento.objects.filter(
            is_deleted=False, cliente=cliente
        )

        result_list = list(chain(requerimentos_cliente, atendimentos_cliente))

        context["title"] = self.title
        context["form_title_identificador"] = f"de CPF nº {self.object.cpf}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = len(result_list)
        context["result_list"] = result_list
        return context


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = ClienteSerializer
    lookup_field = 'cpf'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClienteRetrieveSerializer
        return super().get_serializer_class()

    def get_ordering(self):
        """Retorna a ordenação da requisição ou o padrão."""
        return self.request.query_params.get("ordering", "nome,cpf")

    def get_queryset(self):
        ordering_params = self.get_ordering()

        # Para a ação 'list', tentamos usar o cache com chave dinâmica
        if self.action == 'list':
            version = cache.get_or_set('clientes_list_version_api', 1)
            cache_key = f"lista_de_clientes_api_{ordering_params}_v{version}"
            cached_queryset = cache.get(cache_key)
            if cached_queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                cached_queryset = Cliente.objects.filter(is_deleted=False).order_by(*ordering_params.split(","))
                cache.set(cache_key, cached_queryset, 900)
            else:
                print(f"+++ API CACHE HIT ({cache_key}) +++ Recuperando do Redis.")
            return cached_queryset

        # Para outras ações (retrieve, update, etc.), busca direto do banco sem cache
        return Cliente.objects.filter(is_deleted=False)
