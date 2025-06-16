from datetime import timezone
from rest_framework import serializers
from atendimentos.models import Atendimento


class AtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Atendimento
        fields = '__all__'

    def validate_data(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("A data do atendimento não pode ser maior que a data atual")
        return value


class AtendimentoRetrieveSerializer(serializers.ModelSerializer):
    cliente = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Atendimento
        fields = '__all__'

    def validate_data(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("A data do atendimento não pode ser maior que a data atual")
        return value

    # buscar objeto cliente completo
    def get_cliente(self, obj):
        from clientes.serializers import ClienteSerializer

        cliente = obj.cliente
        return ClienteSerializer(cliente).data
