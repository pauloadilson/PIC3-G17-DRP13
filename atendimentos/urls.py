from django.urls import path, include
from atendimentos.views import (
    AtendimentoCreateListAPIView,
    AtendimentoCreateView,
    AtendimentoDeleteView,
    AtendimentoDetailView,
    AtendimentoRetrieveUpdateDestroyAPIView,
    AtendimentoUpdateView,
    AtendimentosListView,
)


urlpatterns = [
    path("atendimentos", AtendimentosListView.as_view(), name="atendimentos"),
    path("atendimento/", include([
        path("adicionar", AtendimentoCreateView.as_view(), name="adicionar_atendimento",),
        path("<str:cpf>/adicionar", AtendimentoCreateView.as_view(), name="adicionar_atendimento_cliente"),
        path("<str:cpf>/<int:pk>/adicionar", AtendimentoCreateView.as_view(), name="adicionar_atendimento_cliente_requerimento"),
        path("<str:cpf>/<int:pk>", AtendimentoDetailView.as_view(), name="atendimento"),
        path("<str:cpf>/<int:pk>/atualizar", AtendimentoUpdateView.as_view(), name="atualizar_atendimento"),
        path("<str:cpf>/<int:pk>/excluir", AtendimentoDeleteView.as_view(), name="excluir_atendimento"),
    ])),
    path('api/v1/atendimento/', include([
        path("", AtendimentoCreateListAPIView.as_view(), name='atendimento-create-list'),
        path("<int:pk>", AtendimentoRetrieveUpdateDestroyAPIView.as_view(), name='atendimento-detail-update-delete'),
    ])),
]
