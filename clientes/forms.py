from typing import Any, Mapping
from django.utils import timezone
from django import forms
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from clientes.models import (
    Cliente, 
    Atendimento,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Button
from crispy_forms.bootstrap import FormActions


class ClienteModelForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ClienteModelForm, self).__init__(*args, **kwargs)

        # Desabilitar o campo CPF no update
        if self.instance and self.instance.pk:
            self.fields["cpf"].disabled = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('cpf', css_class='form-control'),
            Field('nome', css_class='form-control'),
            Field('data_nascimento', css_class='form-control date_picker', placeholder='dd/mm/aaaa'),
            Field('telefone_whatsapp', css_class='form-control'),
            Field('telefone', css_class='form-control'),
            Field('observacao_telefone', css_class='form-control'),
            Field('email', css_class='form-control', type='email'),
            FormActions(
                Submit("submit", "Salvar", css_class="btn btn-primary"),
                Button(
                    "button",
                    "Voltar",
                    css_class="btn btn-secondary",
                    onclick="window.history.back()",
                ),
            ),
        )

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        clientes = Cliente.objects.all()
        if len(cpf) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos")
        if (
            isinstance(self.instance, Cliente)
            and Cliente.objects.filter(cpf=cpf).exclude(pk=self.instance.pk).exists()
        ):
            raise forms.ValidationError("CPF já cadastrado")
        return cpf

    def save(self, commit=True):
        return super(ClienteModelForm, self).save(commit=commit)



class AtendimentoModelForm(forms.ModelForm):
    class Meta:
        model = Atendimento
        fields = ['data','cliente', 'requerimento','descricao','observacao']

    def __init__(self, *args, **kwargs):
        super(AtendimentoModelForm, self).__init__(*args, **kwargs)

        hoje = timezone.localdate()
        self.initial['data'] = hoje.strftime("%d/%m/%Y")

        if self.initial.get('cliente'):
            self.fields['cliente'].disabled = True

        if self.instance and self.instance.pk:
            self.fields['cliente'].disabled = True
            self.fields['requerimento'].disabled = True

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("data", css_class="form-control date_picker", placeholder="dd/mm/aaaa"),
            Field("cliente", css_class="form-control"),
            Field("requerimento", css_class="form-control"),
            Field("descricao", css_class="form-control", type="email"),
            Field("observacao", css_class="form-control", type="email"),
            FormActions(
                Submit("submit", "Salvar", css_class="btn btn-primary"),
                Button(
                    "button",
                    "Voltar",
                    css_class="btn btn-secondary",
                    onclick="window.history.back()",
                ),
            ),
        )

    def save(self, commit=True):
        return super(AtendimentoModelForm, self).save(commit=commit)
