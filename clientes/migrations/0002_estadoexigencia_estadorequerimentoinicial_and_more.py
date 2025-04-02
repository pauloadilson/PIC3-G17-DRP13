# Generated by Django 5.1.1 on 2024-09-30 02:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoExigencia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(
                    choices=[('em análise', 'Em Análise'), ('concluído', 'Concluído')],
                    max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoRequerimentoInicial',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(
                    choices=[('em análise', 'Em Análise'), ('concluído', 'Concluído')],
                    max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='EstadoRequerimentoRecurso',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(
                    choices=[
                        ('em análise na junta', 'Em Análise na Junta'),
                        ('em análise no conselho', 'Em Análise no Conselho'),
                        ('concluído', 'Concluído')],
                    max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Exigencia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('data', models.DateField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('estado', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='estado_exigencia',
                    to='clientes.estadoexigencia')),
            ],
        ),
        migrations.CreateModel(
            name='Natureza',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='cliente',
            name='observacao_telefone',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='ExigenciaRequerimentoInicial',
            fields=[
                ('exigencia_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='clientes.exigencia')),
            ],
            bases=('clientes.exigencia',),
        ),
        migrations.CreateModel(
            name='ExigenciaRequerimentoRecurso',
            fields=[
                ('exigencia_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='clientes.exigencia')),
            ],
            bases=('clientes.exigencia',),
        ),
        migrations.AddField(
            model_name='exigencia',
            name='natureza',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='natureza_exigencia',
                to='clientes.natureza'),
        ),
        migrations.CreateModel(
            name='Requerimento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('protocolo', models.CharField(max_length=20, unique=True)),
                ('NB', models.CharField(max_length=20)),
                ('requerente_dependentes', models.TextField(blank=True, null=True)),
                ('data', models.DateField()),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('instituidor', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='cliente_instituidor_requerimento',
                    to='clientes.cliente')),
                ('requerente_titular', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name=(
                        'cliente_titular_requerimento'
                    ),
                    to='clientes.cliente')),
                ('tutor_curador', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='cliente_tutor_curador_requerimento',
                    to='clientes.cliente'
                )),
                ('servico', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='servico_requerimento',
                    to='clientes.servico')),
            ],
        ),
        migrations.AddField(
            model_name='exigencia',
            name='requerimento',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='requerimento_exigencia',
                to='clientes.requerimento',
            ),
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('arquivo', models.FileField(upload_to='documentos/')),
                ('nome_arquivo', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cliente_documento', to='clientes.cliente')),
                ('exigencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='exigencia_documento', to='clientes.exigencia')),
                ('requerimento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='requerimento_documento', to='clientes.requerimento')),
            ],
        ),
        migrations.CreateModel(
            name='Atendimento',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('observacao', models.TextField(blank=True, null=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cliente_atendimento', to='clientes.cliente')),
                ('requerimento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='requerimento_atendimento', to='clientes.requerimento')),
            ],
        ),
        migrations.CreateModel(
            name='RequerimentoInicial',
            fields=[
                ('requerimento_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clientes.requerimento')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='estado_requerimento_inicial', to='clientes.estadorequerimentoinicial')),
            ],
            bases=('clientes.requerimento',),
        ),
        migrations.CreateModel(
            name='RequerimentoRecurso',
            fields=[
                ('requerimento_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='clientes.requerimento')),
                ('estado', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='estado_requerimento_recurso', to='clientes.estadorequerimentorecurso')),
            ],
            bases=('clientes.requerimento',),
        ),
    ]
