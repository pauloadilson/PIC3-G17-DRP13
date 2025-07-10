#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cpprev.settings')
django.setup()

from clientes.models import Cliente
from clientes.forms import ClienteModelForm
from datetime import date


def test_soft_delete():
    print("=== TESTE DE SOFT DELETE E REATIVAÇÃO ===")

    # Limpar dados de teste
    Cliente.objects.filter(cpf='12345678901').delete()

    # 1. Criar cliente
    print("\n1. Criando cliente...")
    form_data = {
        'cpf': '12345678901',
        'nome': 'João da Silva',
        'data_nascimento': date(1990, 1, 1),
        'email': 'joao@email.com'
    }

    form = ClienteModelForm(data=form_data)
    if form.is_valid():
        cliente = form.save()
        print(f"✅ Cliente criado: {cliente.nome}")
    else:
        print(f"❌ Erro ao criar: {form.errors}")
        return

    # 2. Soft delete
    print("\n2. Fazendo soft delete...")
    cliente.delete()
    print(f"✅ is_deleted: {cliente.is_deleted}")

    # 3. Tentar recriar
    print("\n3. Tentando recriar com mesmo CPF...")
    form_data2 = {
        'cpf': '12345678901',
        'nome': 'João Santos',
        'data_nascimento': date(1990, 1, 1),
        'email': 'joao.santos@email.com'
    }

    form2 = ClienteModelForm(data=form_data2)
    if form2.is_valid():
        if hasattr(form2, '_reactivating_cliente'):
            print("🔄 REATIVAÇÃO DETECTADA!")

        cliente_salvo = form2.save()
        print(f"✅ Cliente: {cliente_salvo.nome}")
        print(f"✅ is_deleted: {cliente_salvo.is_deleted}")
        print(f"✅ Mesmo ID: {cliente_salvo.cpf == cliente.cpf}")
    else:
        print(f"❌ Erro: {form2.errors}")

    print("\n=== TESTE CONCLUÍDO ===")


if __name__ == "__main__":
    test_soft_delete()
