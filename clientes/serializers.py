from rest_framework import serializers
from .models import Cliente, Atendimento, Requerimento, RequerimentoInicial, RequerimentoRecurso, Servico, EstadoRequerimentoInicial, EstadoRequerimentoRecurso



class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["cpf", "nome", "data_nascimento", "telefone", "observacao_telefone", "telefone_whatsapp", "email"]


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

class RequerimentoSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer()

    class Meta:
        model = Requerimento
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if isinstance(instance, RequerimentoInicial):
            representation['estado'] = EstadoRequerimentoInicialSerializer(instance.estado).data
        elif isinstance(instance, RequerimentoRecurso):
            representation['estado'] = EstadoRequerimentoRecursoSerializer(instance.estado).data
        return representation
        

class AtendimentoSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer()
    requerimento = RequerimentoSerializer()
    
    class Meta:
        model = Atendimento
        fields = ["data", "cliente", "requerimento", "descricao", "observacao"]


class RequerimentoInicialSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer()
    estado = EstadoRequerimentoInicialSerializer()
    
    class Meta:
        model = RequerimentoInicial
        fields = "__all__"
        

class RequerimentoRecursoSerializer(serializers.ModelSerializer):
    servico = ServicoSerializer()
    estado = EstadoRequerimentoRecursoSerializer()
    
    class Meta:
        model = RequerimentoRecurso
        fields = "__all__"