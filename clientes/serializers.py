from rest_framework import serializers
from atendimentos.models import Atendimento
from clientes.models import Cliente
from requerimentos.models import RequerimentoInicial, RequerimentoRecurso
from atendimentos.serializers import AtendimentoSerializer
from requerimentos.serializers import RequerimentoInicialSerializer, RequerimentoRecursoSerializer


class ClienteSerializer(serializers.ModelSerializer):
    quantidade_entidades_dependentes = serializers.SerializerMethodField(read_only=True)
    atendimentos = serializers.SerializerMethodField(read_only=True)
    requerimentos = serializers.SerializerMethodField(read_only=True)
    recursos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_quantidade_entidades_dependentes(self, obj):
        quantidade = obj.total_requerimentos + obj.total_atendimentos
        return quantidade

    def get_atendimentos(self, obj):
        queryset = Atendimento.objects.filter(cliente__cpf=obj.cpf)
        # queryset = obj.cliente_atendimento.filter(is_deleted=False)
        return AtendimentoSerializer(queryset, many=True).data

    def get_requerimentos(self, obj):
        queryset = RequerimentoInicial.objects.filter(requerente_titular__cpf=obj.cpf)
        # queryset = obj.cliente_titular_requerimento.filter(is_deleted=False)
        return RequerimentoInicialSerializer(queryset, many=True).data

    def get_recursos(self, obj):
        queryset = RequerimentoRecurso.objects.filter(requerente_titular__cpf=obj.cpf)
        # queryset = obj.cliente_titular_requerimento.filter(is_deleted=False)
        return RequerimentoRecursoSerializer(queryset, many=True).data
