from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm


from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View
from microsoft_authentication.auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token
from microsoft_authentication.graph_helper import *
from django.contrib import messages
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
    if error != None:
      context['errors'] = []
    context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user',{'is_authenticated': False})
    return context

@method_decorator(login_required(login_url='login'), name='dispatch')
class SignInView(View):
    def get(self, *args, **kwargs):
        # Get the sign-in flow
        flow = get_sign_in_flow()
        # Save the expected flow so we can use it in the callback
        try:
            self.request.session['auth_flow'] = flow
        except Exception as e:
            print(e)
        # Redirect to the Azure sign-in page
        return HttpResponseRedirect(flow['auth_uri'])

class SignOutView(View):
    success_url = reverse_lazy('index')

    def get(self, *args, **kwargs):
        response = HttpResponseRedirect(self.success_url)
        # Clear out the user and token
        remove_user_and_token(self.request)
        return response

@method_decorator(login_required(login_url='login'), name='dispatch')
class CallbackView(View):
    def get(self, *args, **kwargs):
        # Make the token request
        result = get_token_from_code(self.request)
        # Get the user's profile from graph_helper.py script
        user = get_user(result['access_token'])
        # Store user from auth_helper.py script
        store_user(self.request, user)
        messages.success(self.request, 'Login na Microsoft efetuado com sucesso.')
        return HttpResponseRedirect(reverse_lazy('agenda'))