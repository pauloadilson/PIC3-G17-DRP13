from django.contrib import admin
from atendimentos.models import Atendimento

@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'cliente', 'requerimento', 'descricao', 'observacao', 'is_deleted')
    search_fields = ('cpf', 'nome')