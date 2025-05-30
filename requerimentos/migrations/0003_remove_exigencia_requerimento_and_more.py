# Generated by Django 5.1.6 on 2025-04-30 02:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requerimentos', '0002_alter_estadorequerimentoinicial_nome_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='exigencia',
            name='requerimento',
        ),
        migrations.AddField(
            model_name='exigenciarequerimentoinicial',
            name='requerimento',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.PROTECT, related_name='requerimento_inicial_exigencia', to='requerimentos.requerimentoinicial'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exigenciarequerimentorecurso',
            name='requerimento',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, related_name='requerimento_recurso_exigencia', to='requerimentos.requerimentorecurso'),
            preserve_default=False,
        ),
    ]
