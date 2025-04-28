from rest_framework import serializers
from requerimentos.models import EstadoRequerimentoInicial, EstadoRequerimentoRecurso, RequerimentoInicial, RequerimentoRecurso, Servico


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
        fields = [
            "id",
            "protocolo",
            "NB",
            "requerente_dependentes",
            "data",
            "email",
            "observacao",
            "is_deleted",
            "requerente_titular",
            "requerente_titular_nome",
            "servico_nome",
            "tutor_curador",
            "instituidor",
            "estado_nome"]


class RequerimentoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequerimentoRecurso
        fields = [
            "id",
            "protocolo",
            "NB",
            "requerente_dependentes",
            "data",
            "email",
            "observacao",
            "is_deleted",
            "requerente_titular",
            "servico",
            "tutor_curador",
            "instituidor",
            "estado"]
