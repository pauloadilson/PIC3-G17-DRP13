# Generated by Django 5.1.1 on 2024-09-21 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
    ]
