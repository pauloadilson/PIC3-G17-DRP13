from django.urls import path
from django.urls import path, include
from requerimentos.views import (
    MudancaEstadoRequerimentoInicialCreateView,
    MudancaEstadoRequerimentoInicialDeleteView,
    RequerimentoInicialCreateView,
    RequerimentoInicialDetailView,
    RequerimentoInicialUpdateView,
    RequerimentoInicialDeleteView,
    RequerimentoInicialCienciaView,
    RequerimentoRecursoCreateView,
    RequerimentoRecursoDetailView,
    RequerimentoRecursoUpdateView,
    RequerimentoRecursoDeleteView,
    ExigenciaRequerimentoInicialCreateView,
    ExigenciaRequerimentoInicialUpdateView,
    ExigenciaRequerimentoInicialDeleteView,
    ExigenciaRequerimentoRecursoCreateView,
    ExigenciaRequerimentoRecursoUpdateView,
    ExigenciaRequerimentoRecursoDeleteView,
    EscolherTipoRequerimentoView,
    PrazoView,
)

urlpatterns = [
    path('escolher-requerimento/<str:cpf>', EscolherTipoRequerimentoView.as_view(), name='escolher_tipo_requerimento'),
    path("requerimento_inicial/<str:cpf>/", include ([
            path("adicionar", RequerimentoInicialCreateView.as_view(), name="adicionar_requerimento_inicial"),
            path("<int:pk>", RequerimentoInicialDetailView.as_view(), name="requerimento_inicial"),
            path("<int:pk>/atualizar", RequerimentoInicialUpdateView.as_view(), name="atualizar_requerimento_inicial"),
            path("<int:pk>/excluir", RequerimentoInicialDeleteView.as_view(), name="excluir_requerimento_inicial"),
            path("<int:pk>/ciencia", MudancaEstadoRequerimentoInicialCreateView.as_view(), name="ciencia_requerimento_inicial"),
            path("<int:pk>/excluir_mudanca_estado", MudancaEstadoRequerimentoInicialDeleteView.as_view(), name="excluir_mudanca_estado_requerimento_inicial"),
            
    ])),
    path("requerimento_recurso/<str:cpf>/", include ([
            path("adicionar", RequerimentoRecursoCreateView.as_view(), name="adicionar_requerimento_recurso"),
            path("<int:pk>", RequerimentoRecursoDetailView.as_view(), name="requerimento_recurso"),
            path("<int:pk>/atualizar", RequerimentoRecursoUpdateView.as_view(), name="atualizar_requerimento_recurso"),
            path("<int:pk>/excluir", RequerimentoRecursoDeleteView.as_view(), name="excluir_requerimento_recurso"),
    ])),
    path("exigencia_requerimento_inicial/<str:cpf>/<int:pk>/", include ([
            path("adicionar", ExigenciaRequerimentoInicialCreateView.as_view(), name="adicionar_exigencia_requerimento_inicial"),
            path("atualizar", ExigenciaRequerimentoInicialUpdateView.as_view(), name="atualizar_exigencia_requerimento_inicial"),
            path("excluir", ExigenciaRequerimentoInicialDeleteView.as_view(), name="excluir_exigencia_requerimento_inicial"),
    ])),
    path("exigencia_requerimento_recurso/<str:cpf>/<int:pk>/", include ([
            path("adicionar", ExigenciaRequerimentoRecursoCreateView.as_view(), name="adicionar_exigencia_requerimento_recurso"),
            path("atualizar", ExigenciaRequerimentoRecursoUpdateView.as_view(), name="atualizar_exigencia_requerimento_recurso"),
            path("excluir", ExigenciaRequerimentoRecursoDeleteView.as_view(), name="excluir_exigencia_requerimento_recurso"),
    ])),
]
