from datetime import datetime
from django.http import Http404
from django.db.models.base import Model as Model
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
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
    HistoricoMudancaEstadoRequerimentoInicial, 
    Requerimento,
    RequerimentoInicial,
    RequerimentoRecurso,
    Exigencia,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
)
from clientes.forms import (
    AtendimentoModelForm,
    ClienteModelForm,
    EscolhaTipoRequerimentoForm,
    RequerimentoInicialModelForm,
    RequerimentoRecursoModelForm,
    MudancaEstadoRequerimentoInicialForm,
    RequerimentoInicialCienciaForm, 
    RequerimentoInicialModelForm, 
    RequerimentoRecursoModelForm, 
    ExigenciaRequerimentoInicialModelForm,
    ExigenciaRequerimentoRecursoModelForm,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from itertools import chain
from django.utils import timezone

from clientes.serializers import (
    AtendimentoSerializer, 
    ClienteSerializer, 
    #RequerimentoSerializer,
    RequerimentoInicialSerializer, 
    RequerimentoRecursoSerializer,
)

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
            raise Http404("Cliente não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(ClienteDetailView, self).get_context_data(**kwargs)
        cliente_id = self.object.cpf
        title = f"Cliente {cliente_id}"
        requerimentos_cliente = self.object.cliente_titular_requerimento.filter(
            is_deleted=False
        )
        recursos_cliente = self.object.cliente_titular_requerimento.filter(
            is_deleted=False
        )
        atendimentos_cliente = self.object.cliente_atendimento.filter(
            is_deleted=False
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


@method_decorator(login_required(login_url="login"), name="dispatch")
class EscolherTipoRequerimentoView(FormView):
    template_name = "form.html"
    title = "Escolher Tipo de Requerimento"
    form_class = EscolhaTipoRequerimentoForm
    success_url = reverse_lazy("escolher_tipo_requerimento")

    def form_valid(self, form):
        tipo = form.cleaned_data["tipo_requerimento"]
        cpf = cpf = self.kwargs["cpf"]  # Obtendo o CPF do formulário

        # Incluindo o CPF na URL de redirecionamento
        if tipo == "inicial":
            return redirect("adicionar_requerimento_inicial", cpf=cpf)
        elif tipo == "recurso":
            return redirect("adicionar_requerimento_recurso", cpf=cpf)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EscolherTipoRequerimentoView, self).get_context_data(**kwargs)
        # adicionar o título da página e o título do formulário ao contexto
        context["title"] = self.title

        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoInicialCreateView(CreateView):
    model = RequerimentoInicial
    form_class = RequerimentoInicialModelForm
    template_name = "form.html"
    title = "Novo Requerimento"
    form_title_identificador = None

    def get_initial(self):
        initial = super().get_initial()
        # Filtra o cliente titular do requerimento se is_deleted=False
        initial["requerente_titular"] = Cliente.objects.filter(is_deleted=False).get(
            cpf=self.kwargs["cpf"]
        )
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtra os clientes com is_deleted=False para os campos tutor_curador e instituidor
        requerente_titular = self.get_initial().get("requerente_titular")
        form.fields["tutor_curador"].queryset = Cliente.objects.filter(is_deleted=False).exclude(cpf=requerente_titular.cpf)
        form.fields["instituidor"].queryset = Cliente.objects.filter(is_deleted=False).exclude(cpf=requerente_titular.cpf)
        return form

    def form_valid(self, form):
        form.instance.requerente_titular = Cliente.objects.filter(is_deleted=False).get(
            cpf=self.kwargs["cpf"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_inicial",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super(RequerimentoInicialCreateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f'CPF nº {self.kwargs["cpf"]}'
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoRecursoCreateView(CreateView):
    model = RequerimentoRecurso
    form_class = RequerimentoRecursoModelForm
    template_name = "form.html"
    title = "Novo Recurso"
    form_title_identificador = None

    def get_initial(self):
        initial = super().get_initial()
        # Filtra o cliente titular do requerimento se is_deleted=False
        initial["requerente_titular"] = Cliente.objects.filter(
            is_deleted=False
            ).get(
            cpf=self.kwargs["cpf"]
        )
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        requerente_titular = self.get_initial().get("requerente_titular")
        # Filtra os clientes com is_deleted=False para os campos tutor_curador e instituidor
        form.fields["tutor_curador"].queryset = Cliente.objects.filter(
            is_deleted=False
            ).exclude(
                cpf=requerente_titular.cpf
        )
        form.fields["instituidor"].queryset = Cliente.objects.filter(
            is_deleted=False
            ).exclude(
                cpf=requerente_titular.cpf
        )
        return form

    def form_valid(self, form):
        form.instance.requerente_titular = Cliente.objects.filter(is_deleted=False).get(
            cpf=self.kwargs["cpf"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_recurso",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id},
        )

    def get_context_data(self, **kwargs):
        context = super(RequerimentoRecursoCreateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f'CPF nº {self.kwargs["cpf"]}'
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoInicialDetailView(DetailView):
    model = RequerimentoInicial
    template_name = "requerimento.html"
    context_object_name = "requerimento"
    title = "Requerimento"
    paginate_by = 10

    cliente_id = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(RequerimentoInicialDetailView, self).get_context_data(**kwargs)
        
        cliente = self.object.requerente_titular
        exigencias = self.object.requerimento_exigencia.filter(
            is_deleted=False
        )
        historico_mudancas_de_estado = self.object.historico_estado_requerimento.filter(
            is_deleted=False
        )
        qtde_exigencias = self.object.total_exigencias
        qtde_mudancas_estado = self.object.total_mudancas_estado
        qtde_instancias_filhas = qtde_exigencias + qtde_mudancas_estado


        context["title"] = self.title
        context["cliente"] = cliente
        context["exigencias"] = exigencias
        context["historico_mudancas_de_estado"] = historico_mudancas_de_estado
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoRecursoDetailView(DetailView):
    model = RequerimentoRecurso
    template_name = "requerimento.html"
    context_object_name = "requerimento"
    title = "Recurso"
    paginate_by = 10

    cliente_id = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Recurso não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(RequerimentoRecursoDetailView, self).get_context_data(**kwargs)

        cliente = self.object.requerente_titular
        exigencias = self.object.requerimento_exigencia.filter(
            is_deleted=False
        )
        qtde_instancias_filhas = self.object.total_exigencias

        context["title"] = self.title
        context["cliente"] = cliente
        context["exigencias_requerimento"] = exigencias
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoUpdateView(UpdateView):
    model = Requerimento
    template_name = "form.html"
    form_class = None
    title = "Editando Requerimento"
    form_title_identificador = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(RequerimentoUpdateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = (
            f"NB nº {self.object.NB} de {self.object.requerente_titular.nome}"
        )
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoInicialUpdateView(RequerimentoUpdateView):
    model = RequerimentoInicial
    template_name = "form.html"
    form_class = RequerimentoInicialModelForm
    title = "Editando Requerimento Inicial"
    form_title_identificador = "o requerimento inicial"

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_inicial",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id},
        )


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoRecursoUpdateView(RequerimentoUpdateView):
    model = RequerimentoRecurso
    template_name = "form.html"
    form_class = RequerimentoRecursoModelForm
    title = "Editando Recurso"
    form_title_identificador = "o recurso"

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_recurso",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id},
        )


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoInicialDeleteView(DeleteView):
    model = RequerimentoInicial
    template_name = "delete.html"
    title = "Excluindo Requerimento Inicial"
    tipo_objeto = "o requerimento inicial"

    def get_context_data(self, **kwargs):
        context = super(RequerimentoInicialDeleteView, self).get_context_data(**kwargs)
        
        exigencias = self.object.requerimento_exigencia.filter(
            is_deleted=False
        )
        qtde_instancias_filhas = self.object.total_exigencias
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        context["result_list"] = exigencias
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_success_url(self):
        return reverse_lazy(
            "cliente", kwargs={"pk": self.object.requerente_titular.cpf}
        )


@method_decorator(login_required(login_url="login"), name="dispatch")
class RequerimentoRecursoDeleteView(DeleteView):
    model = RequerimentoRecurso
    template_name = "delete.html"
    title = "Excluindo Recurso"
    tipo_objeto = "o recurso"

    def get_context_data(self, **kwargs):
        context = super(RequerimentoRecursoDeleteView, self).get_context_data(**kwargs)

        exigencias = self.object.requerimento_exigencia.filter(
            is_deleted=False
        )
        qtde_instancias_filhas = self.object.total_exigencias

        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        context["result_list"] = exigencias
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_success_url(self):
        return reverse_lazy(
            "cliente", kwargs={"pk": self.object.requerente_titular.cpf}
        )


@method_decorator(login_required(login_url="login"), name="dispatch")
class ExigenciaRequerimentoInicialCreateView(CreateView):
    model = ExigenciaRequerimentoInicial
    template_name = "form.html"
    form_class = ExigenciaRequerimentoInicialModelForm
    title = "Nova Exigência"
    form_title_identificador = None

    def get_initial(self):
        initial = super().get_initial()
        initial["requerimento"] = RequerimentoInicial.objects.filter(
            is_deleted=False
        ).get(id=self.kwargs["pk"])
        return initial

    def form_valid(self, form):
        form.instance.requerimento = RequerimentoInicial.objects.get(
            id=self.kwargs["pk"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_inicial",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super(ExigenciaRequerimentoInicialCreateView, self).get_context_data(
            **kwargs
        )
        context["title"] = self.title
        context["form_title_identificador"] = (
            f'Requerimento de id nº {self.kwargs["pk"]}'
        )
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class ExigenciaRequerimentoRecursoCreateView(CreateView):
    model = ExigenciaRequerimentoRecurso
    template_name = "form.html"
    form_class = ExigenciaRequerimentoRecursoModelForm
    title = "Nova Exigência"
    form_title_identificador = None

    def get_initial(self):
        initial = super().get_initial()
        initial["requerimento"] = RequerimentoRecurso.objects.filter(
            is_deleted=False
        ).get(id=self.kwargs["pk"])
        return initial

    def form_valid(self, form):
        form.instance.requerimento = RequerimentoRecurso.objects.get(
            id=self.kwargs["pk"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_recurso",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super(ExigenciaRequerimentoRecursoCreateView, self).get_context_data(
            **kwargs
        )
        context["title"] = self.title
        context["form_title_identificador"] = f'Recurso de id nº {self.kwargs["pk"]}'
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class ExigenciaRequerimentoInicialUpdateView(UpdateView):
    model = ExigenciaRequerimentoInicial
    template_name = "form.html"
    form_class = ExigenciaRequerimentoInicialModelForm
    title = "Editando"
    form_title_identificador = None

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_inicial",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super(ExigenciaRequerimentoInicialUpdateView, self).get_context_data(
            **kwargs
        )

        context["title"] = self.title
        context["form_title_identificador"] = (
            f"NB nº {self.object.requerimento.NB} de {self.object.requerimento.requerente_titular.nome}"
        )
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj


@method_decorator(login_required(login_url="login"), name="dispatch")
class ExigenciaRequerimentoRecursoUpdateView(UpdateView):
    model = ExigenciaRequerimentoRecurso
    template_name = "form.html"
    form_class = ExigenciaRequerimentoRecursoModelForm
    title = "Editando"
    form_title_identificador = None

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_recurso",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super(ExigenciaRequerimentoRecursoUpdateView, self).get_context_data(
            **kwargs
        )

        context["title"] = self.title
        context["form_title_identificador"] = (
            f"NB nº {self.object.requerimento.NB} de {self.object.requerimento.requerente_titular.nome}"
        )
        return context

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj


@method_decorator(login_required(login_url="login"), name="dispatch")
class ExigenciaRequerimentoInicialDeleteView(DeleteView):
    model = ExigenciaRequerimentoInicial
    template_name = "delete.html"
    title = "Excluindo Exigência do Requerimento"
    tipo_objeto = "a exigência do requerimento"

    def get_context_data(self, **kwargs):
        context = super(ExigenciaRequerimentoInicialDeleteView, self).get_context_data(
            **kwargs
        )
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.requerimento.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = 0
        return context

    def get_success_url(self):
        return reverse_lazy(
            "requerimento_inicial",
            kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]},
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj


@method_decorator(login_required(login_url="login"), name="dispatch")
class ExigenciaRequerimentoRecursoDeleteView(DeleteView):
    model = ExigenciaRequerimentoRecurso
    template_name = "delete.html"
    title = "Excluindo Exigência do Recurso"
    tipo_objeto = "a exigência do recurso"

    def get_context_data(self, **kwargs):
        context = super(ExigenciaRequerimentoRecursoDeleteView, self).get_context_data(
            **kwargs
        )
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.requerimento.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = 0
        return context

    def get_success_url(self):
        return reverse_lazy("requerimento_recurso", kwargs={"cpf":self.kwargs["cpf"],"pk": self.kwargs["pk"]})
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class RequerimentoInicialCienciaView(UpdateView):
    model = RequerimentoInicial
    template_name = "form.html"
    form_class = RequerimentoInicialCienciaForm
    title = "Ciência no Requerimento Inicial"
    form_title_identificador = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_success_url(self):
        return reverse_lazy("requerimento_inicial", kwargs={"cpf":self.kwargs["cpf"],"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(RequerimentoInicialCienciaView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f'NB nº {self.object.NB}'
        return context
    
    def form_valid(self, form):
        requerimento = form.save(commit=False)
        estado_anterior = requerimento.estado
        requerimento.save()
        HistoricoMudancaEstadoRequerimentoInicial.objects.create(
            requerimento=requerimento,
            estado_anterior=estado_anterior,
            estado_novo=requerimento.estado,
            data_mudanca=timezone.now(),
            observacao=requerimento.observacao
        )
        return super().form_valid(form)
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class MudancaEstadoRequerimentoInicialCreateView(CreateView):
    model = HistoricoMudancaEstadoRequerimentoInicial
    template_name = "form.html"
    form_class = MudancaEstadoRequerimentoInicialForm
    title = "Ciência no Requerimento Inicial"
    form_title_identificador = None

    def get_initial(self):
        initial = super().get_initial()
        initial["requerimento"] = RequerimentoInicial.objects.filter(is_deleted=False).get(id=self.kwargs["pk"])
        initial["estado_anterior"] = RequerimentoInicial.objects.filter(is_deleted=False).get(id=self.kwargs["pk"]).estado
        return initial
    
    def form_valid(self, form):
        form.instance.requerimento = RequerimentoInicial.objects.get(id=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("requerimento_inicial", kwargs={"cpf":self.kwargs["cpf"],"pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super(MudancaEstadoRequerimentoInicialCreateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        return context
    
@method_decorator(login_required(login_url='login'), name='dispatch')
class MudancaEstadoRequerimentoInicialDeleteView(DeleteView):
    model = HistoricoMudancaEstadoRequerimentoInicial
    template_name = "delete.html"
    title = "Excluindo Mudança de Estado do Requerimento"
    tipo_objeto = "a mudança de estado do requerimento"

    def get_context_data(self, **kwargs):
        context = super(MudancaEstadoRequerimentoInicialDeleteView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.requerimento.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = 0
        return context
    
    def get_success_url(self):
        return reverse_lazy("requerimento_inicial", kwargs={"cpf":self.kwargs["cpf"],"pk": self.kwargs["pk"]})
    
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


# REST FRAMEWORK API

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


class RequerimentoInicialCreateListAPIView(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = RequerimentoInicial.objects.all()
    serializer_class = RequerimentoInicialSerializer

    def get_queryset(self):
        return RequerimentoInicial.objects.filter(is_deleted=False)
    
    def perform_create(self, serializer):
        serializer.save()

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
        
        
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
# from .serializers import ClienteComRequerimentoSerializer#, RequerimentoSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    lookup_field = 'cpf'

    @action(detail=True, methods=['get'])
    def requerimentos_iniciaisSet(self, request, cpf=None):
        cliente = self.get_object()
        requerimentos_iniciais = RequerimentoInicial.objects.filter(requerente_titular=cliente)
        # requerimentos = cliente.cliente_titular_requerimento.all()
        serializer = RequerimentoInicialSerializer(requerimentos_iniciais, many=True)
        return Response(serializer.data)

class RequerimentoInicialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = RequerimentoInicial.objects.all()
    serializer_class = RequerimentoInicialSerializer