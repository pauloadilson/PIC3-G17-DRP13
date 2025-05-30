# Generated by Django 5.1.1 on 2024-10-20 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Evento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(choices=[
                    ('atendimento', 'Atendimento'),
                    ('pericia', 'Perícia'),
                    ('prazo', 'Prazo')], max_length=20)),
                ('titulo', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_inicio', models.DateTimeField()),
                ('data_fim', models.DateTimeField()),
                ('local', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
    ]
