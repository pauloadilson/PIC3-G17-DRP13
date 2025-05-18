from django.contrib import admin
from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'titulo', 'descricao', 'data_inicio', 'data_fim', 'local')
    list_filter = ('titulo', 'data_inicio', 'local')
    search_fields = ('titulo', 'data_inicio')
