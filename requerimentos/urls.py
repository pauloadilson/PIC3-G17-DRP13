from django.urls import path, include
from requerimentos.views import (
    MudancaEstadoRequerimentoInicialCreateView,
    MudancaEstadoRequerimentoInicialDeleteView,
    RequerimentoInicialCreateListAPIView,
    RequerimentoInicialCreateView,
    RequerimentoInicialDetailView,
    RequerimentoInicialUpdateView,
    RequerimentoInicialDeleteView,
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
)

urlpatterns = [
    path('escolher-requerimento/<str:cpf>', EscolherTipoRequerimentoView.as_view(), name='escolher_tipo_requerimento'),
    path("requerimento_inicial/<str:cpf>/", include([
        path("adicionar", RequerimentoInicialCreateView.as_view(), name="adicionar_requerimento_inicial"),
        path("<int:pk>", RequerimentoInicialDetailView.as_view(), name="requerimento_inicial"),
        path("<int:pk>/atualizar", RequerimentoInicialUpdateView.as_view(), name="atualizar_requerimento_inicial"),
        path("<int:pk>/excluir", RequerimentoInicialDeleteView.as_view(), name="excluir_requerimento_inicial"),
        path("<int:pk>/ciencia", MudancaEstadoRequerimentoInicialCreateView.as_view(), name="ciencia_requerimento_inicial"),
        path("<int:pk>/historico/<int:hist_pk>/excluir", MudancaEstadoRequerimentoInicialDeleteView.as_view(), name="excluir_mudanca_estado_requerimento_inicial"),
    ])),
    path("requerimento_recurso/<str:cpf>/", include([
        path("adicionar", RequerimentoRecursoCreateView.as_view(), name="adicionar_requerimento_recurso"),
        path("<int:pk>", RequerimentoRecursoDetailView.as_view(), name="requerimento_recurso"),
        path("<int:pk>/atualizar", RequerimentoRecursoUpdateView.as_view(), name="atualizar_requerimento_recurso"),
        path("<int:pk>/excluir", RequerimentoRecursoDeleteView.as_view(), name="excluir_requerimento_recurso"),
    ])),
    path("requerimento_inicial/<str:cpf>/<int:pk>/exigencia/", include([
        path("adicionar", ExigenciaRequerimentoInicialCreateView.as_view(), name="adicionar_exigencia_requerimento_inicial"),
        path("<int:exigencia_pk>/atualizar", ExigenciaRequerimentoInicialUpdateView.as_view(), name="atualizar_exigencia_requerimento_inicial"),
        path("<int:exigencia_pk>/excluir", ExigenciaRequerimentoInicialDeleteView.as_view(), name="excluir_exigencia_requerimento_inicial"),
    ])),
    path("requerimento_recurso/<str:cpf>/<int:pk>/exigencia/", include([
        path("adicionar", ExigenciaRequerimentoRecursoCreateView.as_view(), name="adicionar_exigencia_requerimento_recurso"),
        path("<int:exigencia_pk>/atualizar", ExigenciaRequerimentoRecursoUpdateView.as_view(), name="atualizar_exigencia_requerimento_recurso"),
        path("<int:exigencia_pk>/excluir", ExigenciaRequerimentoRecursoDeleteView.as_view(), name="excluir_exigencia_requerimento_recurso"),
    ])),
    path('api/v1/requerimento-inicial/', include([
        path("", RequerimentoInicialCreateListAPIView.as_view(), name='requerimento_inicial-create-list'),
    ])),
]
