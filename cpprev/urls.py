"""
URL configuration for cpprev project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework_nested import routers
from clientes.views import ClienteViewSet
from requerimentos.views import (
    ExigenciaRequerimentoInicialViewSet,
    ExigenciaRequerimentoRecursoViewSet,
    HistoricoMudancaEstadoRequerimentoInicialViewSet,
    HistoricoMudancaEstadoRequerimentoRecursoViewSet,
    RequerimentoInicialViewSet,
    RequerimentoRecursoViewSet,
)
from atendimentos.views import AtendimentoViewSet
from agenda.views import EventoViewSet

# Router principal
router = routers.DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'eventos', EventoViewSet, basename='eventos')
router.register(r'atendimentos', AtendimentoViewSet, basename='atendimentos')
router.register(r'requerimentos-iniciais', RequerimentoInicialViewSet, basename='req_iniciais')
router.register(r'requerimentos-recursos', RequerimentoRecursoViewSet, basename='req_recursos')
router.register(r'exigencias-requerimentos-iniciais', ExigenciaRequerimentoInicialViewSet, basename='exigencias_req_iniciais')
router.register(r'historico-mudancas-requerimentos-iniciais', HistoricoMudancaEstadoRequerimentoInicialViewSet, basename='mudancas_req_iniciais')
router.register(r'exigencias-requerimentos-recursos', ExigenciaRequerimentoInicialViewSet, basename='exigencias_req_recursos')
router.register(r'historico-mudancas-requerimentos-recursos', HistoricoMudancaEstadoRequerimentoInicialViewSet, basename='mudancas_req_recursos')

# Router aninhado para requerimentos
clientes_router = routers.NestedSimpleRouter(router, r'clientes', lookup='cliente')
clientes_router.register(r'requerimentos-iniciais', RequerimentoInicialViewSet, basename='req_iniciais')
clientes_router.register(r'requerimentos-recursos', RequerimentoRecursoViewSet, basename='req_recursos')
clientes_router.register(r'atendimentos', AtendimentoViewSet, basename='atendimentos_cliente')
clientes_req_iniciais_router = routers.NestedSimpleRouter(clientes_router, r'requerimentos-iniciais', lookup='req_inicial')
clientes_req_iniciais_router.register(r'exigencias', ExigenciaRequerimentoInicialViewSet, basename='exigencias_req_iniciais')
clientes_req_iniciais_router.register(r'mudancas-estado', HistoricoMudancaEstadoRequerimentoInicialViewSet, basename='mudancas_req_iniciais')
clientes_req_recursos_router = routers.NestedSimpleRouter(clientes_router, r'requerimentos-recursos', lookup='req_recurso')
clientes_req_recursos_router.register(r'exigencias', ExigenciaRequerimentoRecursoViewSet, basename='exigencias_req_recursos')
clientes_req_recursos_router.register(r'mudancas-estado', HistoricoMudancaEstadoRequerimentoRecursoViewSet, basename='mudancas_req_recursos')

req_iniciais_router = routers.NestedSimpleRouter(router, r'requerimentos-iniciais', lookup='req_inicial')
req_iniciais_router.register(r'exigencias', ExigenciaRequerimentoInicialViewSet, basename='exigencias_req_iniciais')
req_iniciais_router.register(r'mudancas-estado', HistoricoMudancaEstadoRequerimentoInicialViewSet, basename='mudancas_req_iniciais')
req_recursos_router = routers.NestedSimpleRouter(router, r'requerimentos-recursos', lookup='req_recurso')
req_recursos_router.register(r'exigencias', ExigenciaRequerimentoRecursoViewSet, basename='exigencias_req_recursos')
req_recursos_router.register(r'mudancas-estado', HistoricoMudancaEstadoRequerimentoRecursoViewSet, basename='mudancas_req_recursos')


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("clientes.urls")),
    path("", include("requerimentos.urls")),
    path("", include("atendimentos.urls")),
    path("", include("login.urls")),
    path("", include("agenda.urls")),
    path("", include("microsoft_authentication.urls")),
    path("api/v1/", include("cpprev_authentication.urls")),
    path("api/v1/", include(router.urls)),
    path("api/v1/", include(clientes_router.urls)),
    path("api/v1/", include(clientes_req_iniciais_router.urls)),
    path("api/v1/", include(clientes_req_recursos_router.urls)),
    path("api/v1/", include(req_iniciais_router.urls)),
    path("api/v1/", include(req_recursos_router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
