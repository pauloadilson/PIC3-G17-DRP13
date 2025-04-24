from datetime import datetime
from django.views.generic import (
    TemplateView,
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from atendimentos.models import Atendimento
from clientes.models import Cliente
from requerimentos.models import (
    RequerimentoInicial,
    RequerimentoRecurso,
)
from django.urls import reverse_lazy

from django.db.models.functions import ExtractYear, ExtractMonth
from django.db.models import Count
import plotly.express as px


@method_decorator(login_required(login_url="login"), name="dispatch")
class DashboardView(TemplateView):
    template_name = "dashboard.html"
    title = "Painel de Análise"

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super(DashboardView, self).get_context_data(**kwargs)

        ano_atual = datetime.now().year

        total_clientes = Cliente.objects.filter(is_deleted=False).count()
        total_requerimentos = RequerimentoInicial.objects.filter(is_deleted=False).count()
        total_requerimentos_recurso = RequerimentoRecurso.objects.filter(is_deleted=False).count()
        total_atendimentos = Atendimento.objects.filter(is_deleted=False).count()

        context["total_clientes"] = total_clientes
        context["total_requerimentos"] = total_requerimentos
        context["total_requerimentos_recurso"] = total_requerimentos_recurso
        context["total_atendimentos"] = total_atendimentos

        # Gráfico de número de requerimento inicial abertos no ano
        requerimento_inicial_por_mes = RequerimentoInicial.objects.filter(is_deleted=False).filter(data__year=ano_atual).annotate(mes=ExtractMonth('data')).values('mes').annotate(total=Count('id')).order_by('mes')
        meses = [r['mes'] for r in requerimento_inicial_por_mes]
        totais_meses = [r['total'] for r in requerimento_inicial_por_mes]

        # # Gráfico de número de recursos abertos no ano
        # requerimento_recurso_por_mes = RequerimentoRecurso.objects.filter(is_deleted=False).filter(data__year=ano_atual).annotate(mes=ExtractMonth('data')).values('mes').annotate(total=Count('id')).order_by('mes')
        # meses = [r['mes'] for r in requerimento_recurso_por_mes]
        # totais_meses = [r['total'] for r in requerimento_recurso_por_mes]

        fig = px.bar(x=meses, y=totais_meses, labels={'x': 'Mês', 'y': 'Número de Requerimentos'}, title=f'Número de Requerimentos Abertos em {ano_atual}')
        fig.update_xaxes(tickvals=meses)
        fig.update_layout(width=500, height=400)
        chart = fig.to_html()
        context['grafico1'] = chart

        # Gráfico de número de atendimentos realizados no ano
        requerimento_inicial_por_ano = RequerimentoInicial.objects.filter(is_deleted=False).annotate(ano=ExtractYear('data')).values('ano').annotate(total=Count('id')).order_by('ano')
        anos = [r['ano'] for r in requerimento_inicial_por_ano]
        totais_anos = [r['total'] for r in requerimento_inicial_por_ano]

        # # Gráfico de número de atendimentos realizados no ano
        # requerimento_recurso_por_ano = RequerimentoRecurso.objects.filter(is_deleted=False).annotate(ano=ExtractYear('data')).values('ano').annotate(total=Count('id')).order_by('ano')
        # anos = [r['ano'] for r in requerimento_recurso_por_ano]
        # totais_anos = [r['total'] for r in requerimento_recurso_por_ano]

        fig = px.bar(x=anos, y=totais_anos, labels={'x': 'Ano', 'y': 'Número de Requerimentos por ano'}, title='Número de Requerimentos Abertos por Ano')
        fig.update_xaxes(tickvals=anos)
        fig.update_layout(width=500, height=400)
        chart2 = fig.to_html()
        context['grafico2'] = chart2

        context["title"] = self.title
        return context

    def get_success_url(self):
        return reverse_lazy("atendimentos")
