from datetime import timezone
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
        "servico",
        "tutor_curador",
        "instituidor",
        "estado"]

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

