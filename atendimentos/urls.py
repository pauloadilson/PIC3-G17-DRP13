from django.urls import path
from django.urls import path, include
from atendimentos.views import (
    AtendimentoCreateView,
    AtendimentoDeleteView,
    AtendimentoDetailView,
    AtendimentoUpdateView,
    AtendimentosListView,
)

urlpatterns = [
    path("atendimentos", AtendimentosListView.as_view(), name="atendimentos"),
    path("atendimento/",include([
                path("adicionar",AtendimentoCreateView.as_view(), name="adicionar_atendimento",),
                path("<str:cpf>/adicionar",AtendimentoCreateView.as_view(), name="adicionar_atendimento_cliente"),
                path("<str:cpf>/<int:pk>", AtendimentoDetailView.as_view(), name="atendimento"),
                path("<str:cpf>/<int:pk>/atualizar", AtendimentoUpdateView.as_view(), name="atualizar_atendimento"),
                path("<str:cpf>/<int:pk>/excluir", AtendimentoDeleteView.as_view(), name="excluir_atendimento"),
    ])),
]
