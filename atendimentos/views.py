from django.http import Http404
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from atendimentos.models import Atendimento
from clientes.models import Cliente
from atendimentos.forms import AtendimentoModelForm
from django.urls import reverse_lazy
from atendimentos.serializers import AtendimentoSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


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
            raise Http404("Atendimento não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(AtendimentoDetailView, self).get_context_data(**kwargs)

        cliente = self.object.cliente
        requerimento = self.object.requerimento

        context["title"] = self.title
        context["cliente"] = cliente
        context["requerimento"] = requerimento
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


class AtendimentoCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Atendimento.objects.all()
    serializer_class = AtendimentoSerializer

    def get_queryset(self):
        return Atendimento.objects.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save()


class AtendimentoRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Atendimento.objects.all()
    serializer_class = AtendimentoSerializer

    def get_queryset(self):
        return Atendimento.objects.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save()
