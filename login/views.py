from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


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


@method_decorator(login_required(login_url='login'), name='dispatch')
def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = []
    context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context
