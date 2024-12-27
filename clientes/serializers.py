from datetime import timezone
from rest_framework import serializers
from .models import Cliente, Atendimento, RequerimentoInicial, RequerimentoRecurso, Servico, EstadoRequerimentoInicial, EstadoRequerimentoRecurso #, Requerimento



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
        # queryset = Atendimento.objects.filter(cliente__cpf=obj.cpf)
        queryset = obj.cliente_atendimento.filter(is_deleted=False)
        return AtendimentoSerializer(queryset, many=True).data
    
    def get_requerimentos(self, obj):
        queryset = RequerimentoInicial.objects.filter(requerente_titular__cpf=obj.cpf)
        # queryset = obj.cliente_titular_requerimento.filter(is_deleted=False)
        return RequerimentoInicialSerializer(queryset, many=True).data
    
    def get_recursos(self, obj):
        queryset = RequerimentoRecurso.objects.filter(requerente_titular__cpf=obj.cpf)
        # queryset = obj.cliente_titular_requerimento.filter(is_deleted=False)
        return RequerimentoRecursoSerializer(queryset, many=True).data
    
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

# class RequerimentoSerializer(serializers.ModelSerializer):
#     servico = ServicoSerializer()

#     class Meta:
#         model = Requerimento
#         fields = "__all__"

#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         if isinstance(instance, RequerimentoInicial):
#             representation['estado'] = EstadoRequerimentoInicialSerializer(instance.estado).data
#         elif isinstance(instance, RequerimentoRecurso):
#             representation['estado'] = EstadoRequerimentoRecursoSerializer(instance.estado).data
#         return representation
        

class AtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atendimento
        fields = '__all__' 

    def validate_data(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("A data do atendimento não pode ser maior que a data atual")
        return value

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


# class ClienteComRequerimentoSerializer(serializers.ModelSerializer):
#     requerimentos = RequerimentoSerializer(many=True, read_only=True)

#     class Meta:
#         model = Cliente
#         fields = '__all__'