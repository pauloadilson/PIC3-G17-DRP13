from django import forms
from agenda.models import (
    Evento,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Button
from crispy_forms.bootstrap import FormActions


class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['tipo', 'titulo', 'descricao', 'data_inicio', 'local']

    def __init__(self, *args, **kwargs):
        super(EventoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('tipo', css_class='form-control'),
            Field('titulo', css_class='form-control'),
            Field('descricao', css_class='form-control'),
            Field('data_inicio', css_class='form-control date_timepicker_start', placeholder='dd/mm/aaaa hh:mm'),
            # Field('data_fim', css_class='form-control date_timepicker_end', placeholder='dd/mm/aaaa hh:mm'),
            Field('local', css_class='form-control'),
            FormActions(
                Submit('submit', 'Salvar', css_class='btn btn-primary'),
                Button('button', 'Voltar', css_class='btn btn-secondary', onclick='window.history.back()'),
            )
        )
