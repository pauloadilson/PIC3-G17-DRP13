# Generated by Django 5.1.1 on 2025-02-15 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0006_merge_20241109_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atendimento',
            name='data',
            field=models.DateTimeField(),
        ),
    ]
