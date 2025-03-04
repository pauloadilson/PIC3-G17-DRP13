from django.contrib import admin
from clientes.models import Cliente
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cpf', 'nome', 'data_nascimento', 'telefone_whatsapp', 'telefone', 'email', 'is_deleted')
    search_fields = ('cpf', 'nome')
