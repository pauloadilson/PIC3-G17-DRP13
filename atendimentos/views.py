from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from atendimentos.models import Atendimento
from clientes.models import Cliente
from atendimentos.forms import AtendimentoModelForm
from atendimentos.serializers import AtendimentoRetrieveSerializer, AtendimentoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from cpprev.permissions import GlobalDefaultPermission
from requerimentos.models import Requerimento


class AtendimentosListView(LoginRequiredMixin, ListView):
    model = Atendimento
    template_name = "atendimentos.html"
    context_object_name = "atendimentos"
    title = "Atendimentos"
    paginate_by = 10

    def get_ordering(self):
        """Retorna a ordenação da requisição ou o padrão."""
        return self.request.GET.get('ordering', '-data')

    def get_queryset(self):
        ordering_params = self.get_ordering()
        ordering = ordering_params.split(',')

        # Otimiza a consulta para evitar o problema N+1
        base_queryset = self.model.objects.select_related(
            'cliente', 'requerimento'
        ).filter(is_deleted=False)

        version = cache.get_or_set('atendimentos_list_version_html', 1)
        cache_key = f"lista_de_atendimentos_{ordering_params}_v{version}"

        cached_queryset = cache.get(cache_key)
        if cached_queryset is None:
            print(f"--- CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
            cached_queryset = base_queryset.order_by(*ordering)
            cache.set(cache_key, cached_queryset, 900)
        else:
            print(f"+++ CACHE HIT ({cache_key}) +++ Servindo a lista do Redis!")

        return cached_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["current_ordering"] = self.get_ordering()
        return context


class AtendimentoCreateView(LoginRequiredMixin, CreateView):
    model = Atendimento
    template_name = "form.html"
    form_class = AtendimentoModelForm
    title = "Novo Atendimento"

    def get_initial(self):
        initial = super().get_initial()
        # Filtra o cliente titular do requerimento se is_deleted=False
        if "cpf" in self.kwargs:
            initial["cliente"] = Cliente.objects.filter(is_deleted=False).get(
                cpf=self.kwargs["cpf"]
            )
        if "pk" in self.kwargs:
            requerimento = Requerimento.objects.get(
                id=self.kwargs["pk"], is_deleted=False
            )
            initial["requerimento"] = requerimento
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy(
            "atendimento",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id},
        )


class AtendimentoDetailView(LoginRequiredMixin, DetailView):
    model = Atendimento
    template_name = "atendimento.html"
    context_object_name = "atendimento"
    title = "Atendimento"

    cliente_id = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Atendimento não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cliente = self.object.cliente
        requerimento = self.object.requerimento

        context["title"] = self.title
        context["cliente"] = cliente
        context["requerimento"] = requerimento
        return context


class AtendimentoUpdateView(LoginRequiredMixin, UpdateView):
    model = Atendimento
    template_name = "form.html"
    form_class = AtendimentoModelForm
    title = "Editando Atendimento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy(
            "atendimento",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id},
        )


class AtendimentoDeleteView(LoginRequiredMixin, DeleteView):
    model = Atendimento
    template_name = "delete.html"
    title = "Excluindo Atendimento"
    tipo_objeto = "o atendimento"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["tipo_objeto"] = self.tipo_objeto
        return context

    def get_success_url(self):
        return reverse_lazy("atendimentos")


class AtendimentoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = AtendimentoSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AtendimentoRetrieveSerializer
        return super().get_serializer_class()

    def get_ordering(self):
        """Retorna a ordenação da requisição ou o padrão."""
        return self.request.query_params.get("ordering", "-data")

    def get_queryset(self):
        ordering_params = self.get_ordering()
        base_queryset = self.model.objects.select_related('cliente', 'requerimento').filter(is_deleted=False)

        cliente_cpf = self.kwargs.get("cliente_cpf")
        if cliente_cpf:
            return base_queryset.filter(cliente__cpf=cliente_cpf).order_by(*ordering_params.split(','))

        if self.action == "list":
            version = cache.get_or_set('atendimentos_list_version_api', 1)
            cache_key = f"lista_de_atendimentos_api_{ordering_params}_v{version}"
            cached_queryset = cache.get(cache_key)
            if cached_queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                cached_queryset = base_queryset.order_by(*ordering_params.split(','))
                cache.set(cache_key, cached_queryset, 900)
            else:
                print(f"+++ API CACHE HIT ({cache_key}) +++ Recuperando do Redis.")
            return cached_queryset

        return base_queryset
