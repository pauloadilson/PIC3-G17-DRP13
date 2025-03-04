from typing import Any, Mapping
from django.utils import timezone
from django import forms
from django.forms.renderers import BaseRenderer
from django.forms.utils import ErrorList
from atendimentos.models import Atendimento
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Button
from crispy_forms.bootstrap import FormActions


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
