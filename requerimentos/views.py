from django.http import Http404
from django.core.cache import cache
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from clientes.models import Cliente
from cpprev.permissions import GlobalDefaultPermission
from requerimentos.models import (
    HistoricoMudancaEstadoRequerimentoInicial,
    HistoricoMudancaEstadoRequerimentoRecurso,
    Requerimento,
    RequerimentoInicial,
    RequerimentoRecurso,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
)
from requerimentos.forms import (
    EscolhaTipoRequerimentoForm,
    MudancaEstadoRequerimentoRecursoForm,
    RequerimentoInicialModelForm,
    MudancaEstadoRequerimentoInicialForm,
    RequerimentoInicialCienciaForm,
    RequerimentoRecursoCienciaForm,
    RequerimentoRecursoModelForm,
    ExigenciaRequerimentoInicialModelForm,
    ExigenciaRequerimentoRecursoModelForm,
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from requerimentos.serializers import (
    HistoricoMudancaEstadoRequerimentoInicialSerializer,
    HistoricoMudancaEstadoRequerimentoRecursoSerializer,
    RequerimentoInicialRetrieveSerializer,
    RequerimentoInicialSerializer,
    RequerimentoRecursoRetrieveSerializer,
    RequerimentoRecursoSerializer,
    ExigenciaRequerimentoInicialSerializer,
    ExigenciaRequerimentoRecursoSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets


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
        initial["requerente_titular"] = Cliente.objects.filter(is_deleted=False).get(
            cpf=self.kwargs["cpf"]
        )
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtra os clientes com is_deleted=False para os campos tutor_curador e instituidor
        form.fields["tutor_curador"].queryset = Cliente.objects.filter(is_deleted=False)
        form.fields["instituidor"].queryset = Cliente.objects.filter(is_deleted=False)
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

    cliente_id = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(RequerimentoInicialDetailView, self).get_context_data(**kwargs)

        cliente = self.object.requerente_titular
        exigencias = self.object.requerimento_inicial_exigencia.filter(is_deleted=False).filter(requerimento__id=self.object.id)
        historico_mudancas_de_estado = self.object.historico_estado_requerimento.filter(is_deleted=False).filter(requerimento__id=self.object.id)
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

    cliente_id = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Recurso não encontrado")
        return obj

    def get_context_data(self, **kwargs):
        context = super(RequerimentoRecursoDetailView, self).get_context_data(**kwargs)

        cliente = self.object.requerente_titular
        exigencias = self.object.requerimento_recurso_exigencia.filter(
            is_deleted=False
        ).filter(requerimento__id=self.object.id)
        print(exigencias)
        historico_mudancas_de_estado = self.object.historico_estado_requerimento.filter(is_deleted=False).filter(requerimento__id=self.object.id)  # implementar self.object.historico_estado_requerimento.filter(is_deleted=False).filter(requerimento__id=self.object.id)
        qtde_instancias_filhas = self.object.total_exigencias

        context["title"] = self.title
        context["cliente"] = cliente
        context["exigencias"] = exigencias
        context["historico_mudancas_de_estado"] = historico_mudancas_de_estado
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

        exigencias_requerimento = ExigenciaRequerimentoInicial.objects.filter(
            is_deleted=False
        ).filter(requerimento__id=self.object.id)
        qtde_instancias_filhas = self.object.total_exigencias
        result_list = exigencias_requerimento
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        context["result_list"] = result_list
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

        exigencias_requerimento = ExigenciaRequerimentoRecurso.objects.filter(
            is_deleted=False
        ).filter(requerimento__id=self.object.id)
        qtde_instancias_filhas = self.object.total_exigencias
        result_list = exigencias_requerimento

        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = qtde_instancias_filhas
        context["result_list"] = result_list
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
        cpf = self.kwargs.get("cpf")
        pk = self.kwargs.get("pk")
        exigencia_pk = self.kwargs.get("exigencia_pk")
        return get_object_or_404(
            ExigenciaRequerimentoInicial,
            id=exigencia_pk,
            requerimento__id=pk,
            requerimento__requerente_titular__cpf=cpf
        )


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
        cpf = self.kwargs.get("cpf")
        pk = self.kwargs.get("pk")
        exigencia_pk = self.kwargs.get("exigencia_pk")
        return get_object_or_404(
            ExigenciaRequerimentoRecurso,
            id=exigencia_pk,
            requerimento__id=pk,
            requerimento__requerente_titular__cpf=cpf
        )


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
        cpf = self.kwargs.get("cpf")
        pk = self.kwargs.get("pk")
        exigencia_pk = self.kwargs.get("exigencia_pk")
        return get_object_or_404(
            ExigenciaRequerimentoInicial,
            id=exigencia_pk,
            requerimento__id=pk,
            requerimento__requerente_titular__cpf=cpf
        )


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
        return reverse_lazy("requerimento_recurso", kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]})

    def get_object(self, queryset=None):
        cpf = self.kwargs.get("cpf")
        pk = self.kwargs.get("pk")
        exigencia_pk = self.kwargs.get("exigencia_pk")
        return get_object_or_404(
            ExigenciaRequerimentoRecurso,
            id=exigencia_pk,
            requerimento__id=pk,
            requerimento__requerente_titular__cpf=cpf
        )


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
        return reverse_lazy("requerimento_inicial", kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id})

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
        return reverse_lazy("requerimento_inicial", kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]})

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
    slug_field = "hist_pk"
    slug_url_kwarg = "hist_pk"

    def get_context_data(self, **kwargs):
        context = super(MudancaEstadoRequerimentoInicialDeleteView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.requerimento.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = 0
        return context

    def get_success_url(self):
        return reverse_lazy("requerimento_inicial", kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]})

    def get_object(self, queryset=None):
        cpf = self.kwargs.get("cpf")
        pk = self.kwargs.get("pk")
        hist_pk = self.kwargs.get("hist_pk")
        return get_object_or_404(
            HistoricoMudancaEstadoRequerimentoInicial,
            id=hist_pk,
            requerimento__id=pk,
            requerimento__requerente_titular__cpf=cpf
        )


@method_decorator(login_required(login_url='login'), name='dispatch')
class RequerimentoRecursoCienciaView(UpdateView):
    model = RequerimentoRecurso
    template_name = "form.html"
    form_class = RequerimentoRecursoCienciaForm
    title = "Ciência no Recurso"
    form_title_identificador = None

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.is_deleted:
            raise Http404("Requerimento não encontrado")
        return obj

    def get_success_url(self):
        return reverse_lazy("requerimento_recurso", kwargs={"cpf": self.kwargs["cpf"], "pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(RequerimentoRecursoCienciaView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f'NB nº {self.object.NB}'
        return context

    def form_valid(self, form):
        requerimento = form.save(commit=False)
        estado_anterior = requerimento.estado
        requerimento.save()
        HistoricoMudancaEstadoRequerimentoRecurso.objects.create(
            requerimento=requerimento,
            estado_anterior=estado_anterior,
            estado_novo=requerimento.estado,
            data_mudanca=timezone.now(),
            observacao=requerimento.observacao
        )
        return super().form_valid(form)


@method_decorator(login_required(login_url='login'), name='dispatch')
class MudancaEstadoRequerimentoRecursoCreateView(CreateView):
    model = HistoricoMudancaEstadoRequerimentoRecurso
    template_name = "form.html"
    form_class = MudancaEstadoRequerimentoRecursoForm
    title = "Ciência no Recurso"
    form_title_identificador = None

    def get_initial(self):
        initial = super().get_initial()
        initial["requerimento"] = RequerimentoRecurso.objects.filter(is_deleted=False).get(id=self.kwargs["pk"])
        initial["estado_anterior"] = RequerimentoRecurso.objects.filter(is_deleted=False).get(id=self.kwargs["pk"]).estado
        return initial

    def form_valid(self, form):
        form.instance.requerimento = RequerimentoRecurso.objects.get(id=self.kwargs["pk"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("requerimento_recurso", kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super(MudancaEstadoRequerimentoRecursoCreateView, self).get_context_data(**kwargs)
        context["title"] = self.title
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class MudancaEstadoRequerimentoRecursoDeleteView(DeleteView):
    model = HistoricoMudancaEstadoRequerimentoRecurso
    template_name = "delete.html"
    title = "Excluindo Mudança de Estado do Requerimento"
    tipo_objeto = "a mudança de estado do requerimento"
    slug_field = "hist_pk"
    slug_url_kwarg = "hist_pk"

    def get_context_data(self, **kwargs):
        context = super(MudancaEstadoRequerimentoRecursoDeleteView, self).get_context_data(**kwargs)
        context["title"] = self.title
        context["form_title_identificador"] = f"de NB nº {self.object.requerimento.NB}"
        context["tipo_objeto"] = self.tipo_objeto
        context["qtde_instancias_filhas"] = 0
        return context

    def get_success_url(self):
        return reverse_lazy("requerimento_inicial", kwargs={"cpf": self.kwargs["cpf"], "pk": self.kwargs["pk"]})

    def get_object(self, queryset=None):
        cpf = self.kwargs.get("cpf")
        pk = self.kwargs.get("pk")
        hist_pk = self.kwargs.get("hist_pk")
        return get_object_or_404(
            HistoricoMudancaEstadoRequerimentoRecurso,
            id=hist_pk,
            requerimento__id=pk,
            requerimento__requerente_titular__cpf=cpf
        )


class RequerimentoInicialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = RequerimentoInicialSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RequerimentoInicialRetrieveSerializer
        return super().get_serializer_class()
    
    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data,protocolo')
        return ordering.split(',') if ordering else ['-data', 'protocolo']

    def get_queryset(self):
        ordering = self.get_ordering()
        base_queryset = RequerimentoInicial.objects.filter(is_deleted=False)
        cliente_cpf = self.kwargs.get("cliente_cpf")

        # Cache logic ONLY for list view without filters
        if self.action == 'list' and not cliente_cpf:
            cache_key = f"lista_de_requerimentos_iniciais_api_{'_'.join(ordering)}"
            queryset = cache.get(cache_key)
            if queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                queryset = base_queryset.order_by(*ordering)
                TIMEOUT = 900
                cache.set(cache_key, queryset, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'requerimento_inicial_exigencia',
                'historico_estado_requerimento'
            )
        return queryset


class RequerimentoRecursoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = RequerimentoRecursoSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RequerimentoRecursoRetrieveSerializer
        return super().get_serializer_class()
 
    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data,protocolo')
        return ordering.split(',') if ordering else ['-data', 'protocolo']

    def get_queryset(self):
        ordering = self.get_ordering()
        base_queryset = RequerimentoRecurso.objects.filter(is_deleted=False)
        cliente_cpf = self.kwargs.get("cliente_cpf")

        # Cache logic ONLY for list view without filters
        if self.action == 'list' and not cliente_cpf:
            cache_key = f"lista_de_requerimentos_recursos_api_{'_'.join(ordering)}"
            queryset = cache.get(cache_key)
            if queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                queryset = base_queryset.order_by(*ordering)
                TIMEOUT = 900
                cache.set(cache_key, queryset, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")
            return queryset

        # Default behavior for other actions or filtered list
        queryset = base_queryset.order_by(*ordering)
        if cliente_cpf:
            queryset = queryset.filter(requerente_titular__cpf=cliente_cpf)
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related(
                'requerimento_recurso_exigencia',
                'historico_estado_requerimento'
            )
        return queryset


class ExigenciaRequerimentoInicialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = ExigenciaRequerimentoInicialSerializer

    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data')
        return ordering.split(',') if ordering else ['-data']

    def get_queryset(self):
        ordering = self.get_ordering()
        base_queryset = ExigenciaRequerimentoInicial.objects.filter(is_deleted=False)
        requerimento_id = self.kwargs.get("req_inicial_pk")

        # Cache logic ONLY for the global list view (when not nested)
        if self.action == 'list' and not requerimento_id:
            cache_key = f"lista_de_exigencias_iniciais_api_{'_'.join(ordering)}"
            queryset = cache.get(cache_key)
            if queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                queryset = base_queryset.order_by(*ordering)
                TIMEOUT = 900
                cache.set(cache_key, queryset, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")
            return queryset

        # Default behavior for other actions or filtered list
        queryset = base_queryset.order_by(*ordering)
        if requerimento_id:
            queryset = queryset.filter(requerimento__id=requerimento_id)
        return queryset


class ExigenciaRequerimentoRecursoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = ExigenciaRequerimentoRecursoSerializer

    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data')
        return ordering.split(',') if ordering else ['-data']

    def get_queryset(self):
        ordering = self.get_ordering()
        base_queryset = ExigenciaRequerimentoRecurso.objects.filter(is_deleted=False)
        requerimento_id = self.kwargs.get("req_recurso_pk")

        # Cache logic ONLY for the global list view (when not nested)
        if self.action == 'list' and not requerimento_id:
            cache_key = f"lista_de_exigencias_recursos_api_{'_'.join(ordering)}"
            queryset = cache.get(cache_key)
            if queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                queryset = base_queryset.order_by(*ordering)
                TIMEOUT = 900
                cache.set(cache_key, queryset, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")
            return queryset

        # Default behavior for other actions or filtered list
        queryset = base_queryset.order_by(*ordering)
        if requerimento_id:
            queryset = queryset.filter(requerimento__id=requerimento_id)
        return queryset

class HistoricoMudancaEstadoRequerimentoInicialViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = HistoricoMudancaEstadoRequerimentoInicialSerializer

    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data_mudanca')
        return ordering.split(',') if ordering else ['-data_mudanca']

    def get_queryset(self):
        ordering = self.get_ordering()
        base_queryset = HistoricoMudancaEstadoRequerimentoInicial.objects.filter(is_deleted=False)
        requerimento_id = self.kwargs.get("req_inicial_pk")

        # Cache logic ONLY for the global list view (when not nested)
        if self.action == 'list' and not requerimento_id:
            cache_key = f"lista_de_mudancas_de_estado_iniciais_api_{'_'.join(ordering)}"
            queryset = cache.get(cache_key)
            if queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                queryset = base_queryset.order_by(*ordering)
                TIMEOUT = 900
                cache.set(cache_key, queryset, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")
            return queryset

        # Default behavior for other actions or filtered list
        queryset = base_queryset.order_by(*ordering)
        if requerimento_id:
            queryset = queryset.filter(requerimento__id=requerimento_id)
        return queryset


class HistoricoMudancaEstadoRequerimentoRecursoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    queryset = HistoricoMudancaEstadoRequerimentoRecurso.objects.filter(is_deleted=False)
    serializer_class = HistoricoMudancaEstadoRequerimentoRecursoSerializer

    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data_mudanca')
        return ordering.split(',') if ordering else ['-data_mudanca']

    def get_queryset(self):
        ordering = self.get_ordering()
        base_queryset = HistoricoMudancaEstadoRequerimentoRecurso.objects.filter(is_deleted=False)
        requerimento_id = self.kwargs.get("req_recurso_pk")

        # Cache logic ONLY for the global list view (when not nested)
        if self.action == 'list' and not requerimento_id:
            cache_key = f"lista_de_mudancas_de_estado_recursos_api_{'_'.join(ordering)}"
            queryset = cache.get(cache_key)
            if queryset is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                queryset = base_queryset.order_by(*ordering)
                TIMEOUT = 900
                cache.set(cache_key, queryset, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")
            return queryset

        # Default behavior for other actions or filtered list
        queryset = base_queryset.order_by(*ordering)
        if requerimento_id:
            queryset = queryset.filter(requerimento__id=requerimento_id)
        return queryset
