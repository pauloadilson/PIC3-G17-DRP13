from django.urls import path, include
from agenda.views import (
    EventoCreateView,
    AgendaView,
    EventoDetailView,
    PrazoView,
)

urlpatterns = [
    path("agenda/", AgendaView.as_view(), name="agenda"),
    path("evento/", include([
        path("<int:pk>", EventoDetailView.as_view(), name="evento"),
        path("adicionar", EventoCreateView.as_view(), name="adicionar_evento"),
    ])),
    path("prazos", PrazoView.as_view(), name="prazos"),
]
