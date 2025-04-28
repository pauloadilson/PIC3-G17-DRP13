from django.db import models
from django.urls import reverse


class Evento(models.Model):
    TIPO_EVENTO_CHOICES = [
        ('atendimento', 'Atendimento'),
        ('pericia', 'Perícia'),
        ('prazo', 'Prazo'),
    ]

    id = models.AutoField(primary_key=True)  # ID do evento
    tipo = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES)  # Tipo do evento Ex:Atendimento,Pericia,Prazo
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.titulo} ({self.tipo})"

    def get_absolute_url(self):
        return reverse('agenda', kwargs={'pk': self.pk})
