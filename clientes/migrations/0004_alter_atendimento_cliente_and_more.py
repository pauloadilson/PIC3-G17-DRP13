# Generated by Django 5.1.1 on 2024-10-19 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0003_alter_atendimento_cliente_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cliente_atendimento', to='clientes.cliente'),
        ),
        migrations.AlterField(
            model_name='atendimento',
            name='requerimento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='requerimento_atendimento', to='clientes.requerimento'),
        ),
    ]
