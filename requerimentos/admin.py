from django.contrib import admin
from requerimentos.models import (
    HistoricoMudancaEstadoRequerimentoInicial,
    HistoricoMudancaEstadoRequerimentoRecurso,
    Requerimento,
    RequerimentoInicial,
    RequerimentoRecurso,
    EstadoRequerimentoInicial,
    EstadoRequerimentoRecurso,
    Servico,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
    Natureza,
    EstadoExigencia
)


@admin.register(Requerimento)
class RequerimentoAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'NB', 'requerente_titular', 'servico', 'requerente_dependentes', 'tutor_curador', 'instituidor', 'data', 'email', 'observacao', 'is_deleted')
    search_fields = ('NB', 'requerente_titular__nome', 'requererente_titular__cpf')


@admin.register(RequerimentoInicial)
class RequerimentoInicialAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'NB', 'requerente_titular', 'servico', 'requerente_dependentes', 'tutor_curador', 'instituidor', 'data', 'email', 'estado', 'observacao', 'is_deleted')
    search_fields = ('NB', 'requerente_titular__nome', 'requererente_titular__cpf')


@admin.register(EstadoRequerimentoInicial)
class EstadoRequerimentoInicialAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(RequerimentoRecurso)
class RequerimentoRecursoAdmin(admin.ModelAdmin):
    list_display = ('protocolo', 'NB', 'requerente_titular', 'servico', 'requerente_dependentes', 'tutor_curador', 'instituidor', 'data', 'email', 'estado', 'observacao', 'is_deleted')
    search_fields = ('protocolo', 'NB', 'requerente_titular__nome', 'requererente_titular__cpf')


@admin.register(EstadoRequerimentoRecurso)
class EstadoRequerimentoRecursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(ExigenciaRequerimentoInicial)
class ExigenciaRequerimentoInicialAdmin(admin.ModelAdmin):
    list_display = ('id', 'requerimento', 'natureza', 'estado', 'is_deleted')
    search_fields = ('NB',)  # 'NB__requerente_titular__nome', 'NB__requerente_titular__cpf


@admin.register(ExigenciaRequerimentoRecurso)
class ExigenciaRequerimentoRecursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'requerimento', 'natureza', 'estado', 'is_deleted')
    search_fields = ('NB',)  # 'NB__requerente_titular__nome', 'NB__requerente_titular__cpf


@admin.register(EstadoExigencia)
class EstadoExigenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(Natureza)
class NaturezaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(HistoricoMudancaEstadoRequerimentoInicial)
class HistoricoMudancaEstadoRequerimentoInicialAdmin(admin.ModelAdmin):
    list_display = ('id', 'requerimento', 'estado_anterior', 'estado_novo', 'data_mudanca', 'observacao')
    search_fields = ('requerimento__NB', 'requerimento__requerente_titular__nome', 'requerimento__requerente_titular__cpf')


@admin.register(HistoricoMudancaEstadoRequerimentoRecurso)
class HistoricoMudancaEstadoRequerimentoRecursoAdmin(admin.ModelAdmin):
    list_display = ('id', 'requerimento', 'estado_anterior', 'estado_novo', 'data_mudanca', 'observacao')
    search_fields = ('requerimento__NB', 'requerimento__requerente_titular__nome', 'requerimento__requerente_titular__cpf')
