from datetime import datetime
from django.http import Http404
from django.db.models.base import Model as Model
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from agenda.models import Evento
from clientes.models import (
    Atendimento,
    Cliente,
)
from requerimentos.models import (
    RequerimentoInicial,
    RequerimentoRecurso,
)
from clientes.forms import (
    AtendimentoModelForm,
    ClienteModelForm,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from itertools import chain
from django.utils import timezone
# Create your views here.
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
            raise Http404("Requerimento não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(ClienteDetailView, self).get_context_data(**kwargs)
        cliente_id = self.object.cpf
        title = f"Cliente {cliente_id}"
        requerimentos_cliente = RequerimentoInicial.objects.filter(
            is_deleted=False
        ).filter(requerente_titular__cpf__icontains=cliente_id)
        recursos_cliente = RequerimentoRecurso.objects.filter(is_deleted=False).filter(
            requerente_titular__cpf__icontains=cliente_id
        )
        atendimentos_cliente = Atendimento.objects.filter(is_deleted=False).filter(
            cliente__cpf__icontains=cliente_id
        )
        qtde_instancias_filhas = self.object.total_requerimentos + self.object.total_atendimentos

        context["title"] = title
        context["requerimentos"] = requerimentos_cliente
        context["recursos"] = recursos_cliente
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
        return reverse_lazy("cliente", kwargs={"pk": self.object.cpf})

    def get_context_data(self, **kwargs):
        context = super(ClienteUpdateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f"CPF nº {self.object.cpf}"
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
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
            raise Http404("Requerimento não encontrado")
        return obj

@method_decorator(login_required(login_url="login"), name="dispatch")
class PrazoView(TemplateView):
    template_name = "prazo.html"
    title = "Prazo"

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super(PrazoView, self).get_context_data(**kwargs)
        hoje = timezone.localdate()
        hoje_aware = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
        eventos = Evento.objects.filter(
            data_inicio__gte=hoje_aware,
            ).filter(
            tipo="prazo",
            ).order_by('data_inicio')[:5]
        context["title"] = self.title
        context["agenda"] = eventos
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class AtendimentosListView(ListView):
    model = Atendimento
    template_name = "atendimentos.html"
    context_object_name = "atendimentos"
    title = "Atendimentos"
    ordering = ["data"]
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class AtendimentoCreateView(CreateView):
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
        return initial

    def get_context_data(self, **kwargs):
        context = super(AtendimentoCreateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy("atendimentos")


@method_decorator(login_required(login_url="login"), name="dispatch")
class AtendimentoDetailView(DetailView):
    model = Atendimento
    template_name = "atendimento.html"
    context_object_name = "atendimento"
    title = "Atendimento"

    cliente_id = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(AtendimentoDetailView, self).get_context_data(**kwargs)
        
        cliente_id = self.object.cliente.cpf
        cliente = Cliente.objects.filter(is_deleted=False).filter(
            cpf__icontains=cliente_id
        )[
            0
        ]  # .order_by('nome') '-nome' para ordem decrescente

        context["title"] = self.title
        context["cliente"] = cliente
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class AtendimentoUpdateView(UpdateView):
    model = Atendimento
    template_name = "form.html"
    form_class = AtendimentoModelForm
    title = "Editando Atendimento"

    def get_context_data(self, **kwargs):
        context = super(AtendimentoUpdateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy("atendimentos")


@method_decorator(login_required(login_url="login"), name="dispatch")
class AtendimentoDeleteView(DeleteView):
    model = Atendimento
    template_name = "delete.html"
    success_url = reverse_lazy("atendimentos")
    title = "Excluindo Atendimento"
    tipo_objeto = "o atendimento"
    is_atendimento = True

    def get_context_data(self, **kwargs):
        context = super(AtendimentoDeleteView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["tipo_objeto"] = self.tipo_objeto
        context["is_atendimento"] = self.is_atendimento
        return context

    def get_success_url(self):
        return reverse_lazy("atendimentos")
