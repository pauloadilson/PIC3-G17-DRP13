from rest_framework import serializers
from requerimentos.models import (
    EstadoRequerimentoInicial,
    EstadoRequerimentoRecurso,
    ExigenciaRequerimentoInicial,
    ExigenciaRequerimentoRecurso,
    HistoricoMudancaEstadoRequerimentoInicial,
    HistoricoMudancaEstadoRequerimentoRecurso,
    RequerimentoInicial,
    RequerimentoRecurso,
    Servico,
)


class EstadoRequerimentoInicialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoRequerimentoInicial
        fields = '__all__'


class EstadoRequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoRequerimentoRecurso
        fields = '__all__'


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = '__all__'


class RequerimentoInicialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequerimentoInicial
        fields = '__all__'


class RequerimentoInicialRetrieveSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer(read_only=True)
    estado = EstadoRequerimentoInicialSerializer(read_only=True)

    quantidade_entidades_dependentes = serializers.SerializerMethodField(read_only=True)
    exigencias = serializers.SerializerMethodField(read_only=True)
    mudancas_estado = serializers.SerializerMethodField(read_only=True)
    requerente_titular = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RequerimentoInicial
        fields = '__all__'

    def get_quantidade_entidades_dependentes(self, obj):
        quantidade = obj.total_exigencias + obj.total_mudancas_estado
        return quantidade

    def get_exigencias(self, obj):
        queryset = ExigenciaRequerimentoInicial.objects.filter(requerimento__id=obj.id)
        return ExigenciaRequerimentoInicialSerializer(queryset, many=True).data

    def get_mudancas_estado(self, obj):
        queryset = HistoricoMudancaEstadoRequerimentoInicial.objects.filter(requerimento__id=obj.id)
        return HistoricoMudancaEstadoRequerimentoInicialSerializer(queryset, many=True).data

    def get_requerente_titular(self, obj):
        from clientes.serializers import ClienteSerializer

        queryset = obj.requerente_titular
        return ClienteSerializer(queryset).data


class RequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequerimentoRecurso
        fields = '__all__'


class RequerimentoRecursoRetrieveSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer(read_only=True)
    estado = EstadoRequerimentoRecursoSerializer(read_only=True)

    quantidade_entidades_dependentes = serializers.SerializerMethodField(read_only=True)
    exigencias = serializers.SerializerMethodField(read_only=True)
    mudancas_estado = serializers.SerializerMethodField(read_only=True)
    requerente_titular = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RequerimentoRecurso
        fields = '__all__'

    def get_quantidade_entidades_dependentes(self, obj):
        quantidade = obj.total_exigencias + obj.total_mudancas_estado
        return quantidade

    def get_exigencias(self, obj):
        queryset = ExigenciaRequerimentoRecurso.objects.filter(requerimento__id=obj.id)
        return ExigenciaRequerimentoRecursoSerializer(queryset, many=True).data

    def get_mudancas_estado(self, obj):
        queryset = HistoricoMudancaEstadoRequerimentoRecurso.objects.filter(requerimento__id=obj.id)
        return HistoricoMudancaEstadoRequerimentoRecursoSerializer(queryset, many=True).data

    def get_requerente_titular(self, obj):
        from clientes.serializers import ClienteSerializer

        queryset = obj.requerente_titular
        return ClienteSerializer(queryset).data


class ExigenciaRequerimentoInicialSerializer(serializers.ModelSerializer):
    natureza_nome = serializers.CharField(source='natureza.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)

    class Meta:
        model = ExigenciaRequerimentoInicial
        fields = '__all__'


class ExigenciaRequerimentoRecursoSerializer(serializers.ModelSerializer):
    natureza_nome = serializers.CharField(source='natureza.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)

    class Meta:
        model = ExigenciaRequerimentoRecurso
        fields = '__all__'


class HistoricoMudancaEstadoRequerimentoInicialSerializer(serializers.ModelSerializer):
    estado_anterior_nome = serializers.CharField(source='estado_anterior.nome', read_only=True)
    estado_novo_nome = serializers.CharField(source='estado_novo.nome', read_only=True)
    requerimento_nome = serializers.CharField(source='requerimento.nome', read_only=True)
    requerimento_servico_nome = serializers.CharField(source='requerimento.servico.nome', read_only=True)

    class Meta:
        model = HistoricoMudancaEstadoRequerimentoInicial
        fields = '__all__'


class HistoricoMudancaEstadoRequerimentoRecursoSerializer(serializers.ModelSerializer):
    estado_anterior_nome = serializers.CharField(source='estado_anterior.nome', read_only=True)
    estado_novo_nome = serializers.CharField(source='estado_novo.nome', read_only=True)
    requerimento_nome = serializers.CharField(source='requerimento.nome', read_only=True)
    requerimento_servico_nome = serializers.CharField(source='requerimento.servico.nome', read_only=True)

    class Meta:
        model = HistoricoMudancaEstadoRequerimentoRecurso
        fields = '__all__'
