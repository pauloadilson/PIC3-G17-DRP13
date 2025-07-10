from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginView(LoginView):
    form_class = AuthenticationForm  # Utilizando o formulário padrão de autenticação
    template_name = 'login.html'  # Template que será renderizado
    redirect_authenticated_user = True
    title = "Login"  # Título da página
    success_url = reverse_lazy('index')  # Página para onde o usuário será redirecionado após o login

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context
