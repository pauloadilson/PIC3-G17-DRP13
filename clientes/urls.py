from django.urls import path, include
from clientes.views import (
    AtendimentoCreateListAPIView,
    AtendimentoRetrieveUpdateDestroyAPIView,
    AtendimentoCreateView,
    AtendimentoDeleteView,
    AtendimentoDetailView,
    AtendimentoUpdateView,
    AtendimentosListView,
    ClienteCreateListAPIView,
    ClienteRetrieveUpdateDestroyAPIView,
    IndexView,
    ClientesListView,
    ClienteCreateView,
    ClienteDetailView,
    ClienteUpdateView,
    ClienteDeleteView,
    MudancaEstadoRequerimentoInicialCreateView,
    MudancaEstadoRequerimentoInicialDeleteView,
    RequerimentoInicialCreateListAPIView,
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

from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, RequerimentoInicialViewSet

router = DefaultRouter()
router.register(r'clientesSet', ClienteViewSet)
router.register(r'requerimentos_iniciaisSet', RequerimentoInicialViewSet)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("clientes/", ClientesListView.as_view(), name="clientes"),
    path("cliente/", include ([
        path('adicionar', ClienteCreateView.as_view(), name='adicionar_cliente'),
        path('<str:cpf>', ClienteDetailView.as_view(), name='cliente'),
        path('<str:cpf>/atualizar', ClienteUpdateView.as_view(), name='atualizar_cliente'),
        path('<str:cpf>/excluir', ClienteDeleteView.as_view(), name='excluir_cliente'),
    ])),
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
    path("atendimentos", AtendimentosListView.as_view(), name="atendimentos"),
    path("atendimento/",include([
                path("adicionar",AtendimentoCreateView.as_view(), name="adicionar_atendimento",),
                path("<str:cpf>/adicionar",AtendimentoCreateView.as_view(), name="adicionar_atendimento_cliente"),
                path("<str:cpf>/<int:pk>", AtendimentoDetailView.as_view(), name="atendimento"),
                path("<str:cpf>/<int:pk>/atualizar", AtendimentoUpdateView.as_view(), name="atualizar_atendimento"),
                path("<str:cpf>/<int:pk>/excluir", AtendimentoDeleteView.as_view(), name="excluir_atendimento"),
    ])),
    path("prazos", PrazoView.as_view(), name="prazos"),
    path('api/v1/clientes/', include ([
            path("", ClienteCreateListAPIView.as_view(), name='cliente-create-list'),
            path("<str:cpf>", ClienteRetrieveUpdateDestroyAPIView.as_view(), name='cliente-detail-update-delete'),
    ])),
        path('api/v1/requerimento-inicial/', include ([
            path("", RequerimentoInicialCreateListAPIView.as_view(), name='requerimento_inicial-create-list'),
        #     path("<int:pk>", ClienteRetrieveUpdateDestroyAPIView.as_view(), name='cliente-detail-update-delete'),
    ])),
        path('api/v1/atendimento/', include ([
            path("", AtendimentoCreateListAPIView.as_view(), name='atendimento-create-list'),
            path("<int:pk>", AtendimentoRetrieveUpdateDestroyAPIView.as_view(), name='atendimento-detail-update-delete'),
    ])),
    path('api/v1/', include(router.urls)),
]
