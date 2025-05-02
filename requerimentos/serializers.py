from rest_framework import serializers
from requerimentos.models import EstadoRequerimentoInicial, EstadoRequerimentoRecurso, ExigenciaRequerimentoInicial, ExigenciaRequerimentoRecurso, HistoricoMudancaEstadoRequerimentoInicial, HistoricoMudancaEstadoRequerimentoRecurso, RequerimentoInicial, RequerimentoRecurso, Servico


class EstadoRequerimentoInicialSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoRequerimentoInicial
        fields = ["nome"]


class EstadoRequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoRequerimentoRecurso
        fields = ["nome"]


class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ["nome"]


class RequerimentoInicialSerializer(serializers.ModelSerializer):
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)
    requerente_titular_nome = serializers.CharField(source='requerente_titular.nome', read_only=True)

    class Meta:
        model = RequerimentoInicial
        fields = '__all__'


class RequerimentoInicialCompletoSerializer(serializers.ModelSerializer):
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)
    requerente_titular_nome = serializers.CharField(source='requerente_titular.nome', read_only=True)

    quantidade_entidades_dependentes = serializers.SerializerMethodField(read_only=True)
    exigencias = serializers.SerializerMethodField(read_only=True)
    mudancas_estado = serializers.SerializerMethodField(read_only=True)

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


class RequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequerimentoRecurso
        fields = '__all__'


class RequerimentoRecursoCompletoSerializer(serializers.ModelSerializer):
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    estado_nome = serializers.CharField(source='estado.nome', read_only=True)
    requerente_titular_nome = serializers.CharField(source='requerente_titular.nome', read_only=True)

    quantidade_entidades_dependentes = serializers.SerializerMethodField(read_only=True)
    exigencias = serializers.SerializerMethodField(read_only=True)
    mudancas_estado = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RequerimentoRecurso
        fields = '__all__'  # + "requerente_titular_nome" + "servico_nome" + "estado_nome" + "exigencias" + "mudancas_estado" + "quantidade_entidades_dependentes"

    def get_quantidade_entidades_dependentes(self, obj):
        quantidade = obj.total_exigencias + obj.total_mudancas_estado
        return quantidade

    def get_exigencias(self, obj):
        queryset = ExigenciaRequerimentoRecurso.objects.filter(requerimento__id=obj.id)
        return ExigenciaRequerimentoRecursoSerializer(queryset, many=True).data

    def get_mudancas_estado(self, obj):
        queryset = HistoricoMudancaEstadoRequerimentoRecurso.objects.filter(requerimento__id=obj.id)
        return HistoricoMudancaEstadoRequerimentoRecursoSerializer(queryset, many=True).data


class ExigenciaRequerimentoInicialSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExigenciaRequerimentoInicial
        fields = [
            "id",
            "requerimento",
            "data",
            "natureza",
            "estado"
        ]


class ExigenciaRequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExigenciaRequerimentoRecurso
        fields = [
            "id",
            "requerimento",
            "data",
            "natureza",
            "estado"
        ]


class HistoricoMudancaEstadoRequerimentoInicialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoMudancaEstadoRequerimentoInicial
        fields = [
            "id",
            "requerimento",
            "estado_anterior",
            "estado_novo",
            "observacao",
            "data_mudanca"
        ]


class HistoricoMudancaEstadoRequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoMudancaEstadoRequerimentoRecurso
        fields = [
            "id",
            "requerimento",
            "estado_anterior",
            "estado_novo",
            "observacao",
            "data_mudanca"
        ]
