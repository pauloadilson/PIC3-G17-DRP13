# Generated by Django 5.1.1 on 2024-11-03 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0004_atendimento_is_deleted_documento_is_deleted_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requerimento',
            name='NB',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
