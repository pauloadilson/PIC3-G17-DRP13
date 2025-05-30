# Generated by Django 5.1.6 on 2025-04-16 12:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requerimentos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='estadorequerimentoinicial',
            name='nome',
            field=models.CharField(choices=[('em análise', 'Em Análise'), ('aguardando cumprimento de exigência', 'Aguardando Cumprimento de Exigência'), ('concluído deferido', 'Concluído Deferido'), ('concluído indeferido', 'Concluído Indeferido')], max_length=100),
        ),
        migrations.AlterField(
            model_name='estadorequerimentorecurso',
            name='nome',
            field=models.CharField(choices=[('em análise na junta', 'Em Análise na Junta'), ('em análise no conselho', 'Em Análise no Conselho'), ('concluído deferido', 'Concluído Deferido'), ('concluído indeferido', 'Concluído Indeferido')], max_length=30),
        ),
        migrations.CreateModel(
            name='HistoricoMudancaEstadoRequerimentoRecurso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('data_mudanca', models.DateTimeField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('estado_anterior', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estado_anterior', to='requerimentos.estadorequerimentorecurso')),
                ('estado_novo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='estado_novo', to='requerimentos.estadorequerimentorecurso')),
                ('requerimento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='historico_estado_requerimento', to='requerimentos.requerimentorecurso')),
            ],
        ),
    ]
