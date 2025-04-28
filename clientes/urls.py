from django.urls import path, include
from clientes.views import (
    IndexView,
    ClientesListView,
    ClienteCreateView,
    ClienteDetailView,
    ClienteUpdateView,
    ClienteDeleteView,
)

from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, RequerimentoInicialViewSet

router = DefaultRouter()
router.register(r'clientesSet', ClienteViewSet)
router.register(r'requerimentos_iniciaisSet', RequerimentoInicialViewSet)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("clientes/", ClientesListView.as_view(), name="clientes"),
    path("cliente/", include([
        path('adicionar', ClienteCreateView.as_view(), name='adicionar_cliente'),
        path('<str:cpf>', ClienteDetailView.as_view(), name='cliente'),
        path('<str:cpf>/atualizar', ClienteUpdateView.as_view(), name='atualizar_cliente'),
        path('<str:cpf>/excluir', ClienteDeleteView.as_view(), name='excluir_cliente'),
    ])),
    path('api/v1/', include(router.urls)),
]
