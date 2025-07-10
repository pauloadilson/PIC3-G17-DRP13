from django import forms
from clientes.models import Cliente
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Button
from crispy_forms.bootstrap import FormActions


class ClienteModelForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["cpf", "nome", "data_nascimento", "telefone", "observacao_telefone", "telefone_whatsapp", "email"]

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
        if not cpf or len(cpf) != 11:
            raise forms.ValidationError("CPF deve conter 11 dígitos")

        # Para edição: verifica se existe outro cliente ativo com o mesmo CPF
        if self.instance.pk:
            if Cliente.objects.filter(cpf=cpf, is_deleted=False).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("CPF já cadastrado")
        else:
            # Para criação: verifica se existe um cliente ativo com o mesmo CPF
            if Cliente.objects.filter(cpf=cpf, is_deleted=False).exists():
                raise forms.ValidationError("CPF já cadastrado")

            # Verifica se existe um cliente soft deleted para reativação
            deleted_cliente = Cliente.objects.filter(cpf=cpf, is_deleted=True).first()
            if deleted_cliente:
                self._reactivating_cliente = deleted_cliente

        return cpf

    def validate_unique(self):
        """
        Sobrescreve a validação de unicidade padrão do Django
        para considerar apenas clientes não soft deleted
        """
        exclude = self._get_validation_exclusions()

        # Para criação, ignora validação se há um cliente soft deleted
        if not self.instance.pk:
            cpf = self.cleaned_data.get('cpf')
            if cpf and Cliente.objects.filter(cpf=cpf, is_deleted=True).exists():
                # Se existe um soft deleted, não valida unicidade
                return

        # Para outros casos, chama a validação padrão mas apenas para clientes ativos
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            # Se o erro é de unicidade do CPF, verifica se é por causa de soft deleted
            if 'cpf' in e.error_dict:
                cpf = self.cleaned_data.get('cpf')
                if cpf:
                    # Se existe apenas cliente soft deleted, ignora o erro
                    active_cliente = Cliente.objects.filter(cpf=cpf, is_deleted=False)
                    if self.instance.pk:
                        active_cliente = active_cliente.exclude(pk=self.instance.pk)

                    if not active_cliente.exists():
                        return  # Não há conflito real

            # Para outros erros, propaga normalmente
            self._update_errors(e)

    def save(self, commit=True):
        # Se estamos criando um novo cliente
        if not self.instance.pk:
            cpf = self.cleaned_data.get('cpf')
            # Verifica se existe um cliente soft deleted com o mesmo CPF
            deleted_cliente = Cliente.objects.filter(cpf=cpf, is_deleted=True).first()
            if deleted_cliente:
                # Reativa o cliente existente ao invés de criar um novo
                for field_name, field_value in self.cleaned_data.items():
                    if field_name != 'cpf':  # CPF já é o mesmo
                        setattr(deleted_cliente, field_name, field_value)
                deleted_cliente.is_deleted = False
                if commit:
                    deleted_cliente.save()
                return deleted_cliente

        return super(ClienteModelForm, self).save(commit=commit)
