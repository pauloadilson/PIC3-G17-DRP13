from django.urls import path
from django.urls import path, include
from clientes.views import (
    AtendimentoCreateView,
    AtendimentoDeleteView,
    AtendimentoDetailView,
    AtendimentoUpdateView,
    AtendimentosListView,
    IndexView,
    ClientesListView,
    ClienteCreateView,
    ClienteDetailView,
    ClienteUpdateView,
    ClienteDeleteView,
    PrazoView,
)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("clientes/", ClientesListView.as_view(), name="clientes"),
    path("cliente/", include ([
        path('adicionar', ClienteCreateView.as_view(), name='adicionar_cliente'),
        path('<str:cpf>', ClienteDetailView.as_view(), name='cliente'),
        path('<str:cpf>/atualizar', ClienteUpdateView.as_view(), name='atualizar_cliente'),
        path('<str:cpf>/excluir', ClienteDeleteView.as_view(), name='excluir_cliente'),
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
]
