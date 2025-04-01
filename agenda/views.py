from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
from django.views import View
from django.views.generic import (
    TemplateView,
    ListView,
    CreateView,
    UpdateView,
)
from agenda.models import Evento
from django.urls import reverse_lazy
from agenda.forms import EventoForm
from microsoft_authentication.graph_helper import criar_evento_no_microsoft_graph
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pytz
from microsoft_authentication.auth_helper import get_token


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaView(ListView):
    model = Evento
    template_name = 'agenda.html'
    context_object_name = 'agenda'
    title = "Agenda"

    def get_queryset(self):
        return Evento.objects.all()

    def get_context_data(self, **kwargs):
        context = super(AgendaView, self).get_context_data(**kwargs)
        token = get_token(self.request)
        context['is_microsoft_logged_in'] = bool(token)
        context['title'] = self.title
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class EventoCreateView(CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'form.html'
    success_url = reverse_lazy('agenda')
    title = "Novo Evento"

    def form_valid(self, form):
        # Primeiro, salva o evento localmente
        response = super().form_valid(form)
        print('entrando no metodo')
        # Depois, tenta criar o evento no Microsoft Graph
        try:
            print('tentando criar evento no Microsoft Graph')
            # Substitua "user_email" pelo e-mail do usuário que deve receber o evento
            # user_email = settings.MICROSOFT_CLIENT_EMAIL  # Exemplo usando o e-mail do usuário logado
            criar_evento_no_microsoft_graph(self.request, self.object)  # self.object é o evento salvo
            messages.success(self.request, 'Evento criado e sincronizado com o calendário do Microsoft Outlook.')
        except Exception:
            messages.error(self.request, 'Erro ao criar evento no Microsoft Calendar! \
                Realize a inclusão manualmente no Microsoft Outlook.')
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, 'Erro ao criar evento: form_invalid.')
        return response

    def get_context_data(self, **kwargs):
        context = super(EventoCreateView, self).get_context_data(**kwargs)
        # adicionar o título da página e o título do formulário ao contexto
        context['title'] = self.title
        return context


@method_decorator(login_required(login_url='login'), name='dispatch')
class EventoDetailView(View):
    def get(self, request, pk):
        evento = get_object_or_404(Evento, id=pk)

        # Defina o fuso horário UTC-3 'America/Sao_Paulo'
        timezone = pytz.timezone('America/Sao_Paulo')
        # Converta as datas e horas para o fuso horário UTC-3
        data_inicio = evento.data_inicio.astimezone(timezone)

        data = {
            'titulo': evento.titulo,
            'tipo': evento.tipo.capitalize(),
            'descricao': evento.descricao,
            'data_inicio': data_inicio.strftime('%d/%m/%Y às %H:%M'),
            'local': evento.local,
        }
        return JsonResponse(data)


@method_decorator(login_required(login_url='login'), name='dispatch')
class EventoUpdateView(UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'form.html'
    success_url = reverse_lazy('agenda')
    title = "Editando Evento"

    def get_context_data(self, **kwargs):
        context = super(EventoUpdateView, self).get_context_data(**kwargs)
        # adicionar o título da página e o título do formulário ao contexto
        context['title'] = self.title
        return context


@method_decorator(login_required(login_url="login"), name="dispatch")
class PrazoView(TemplateView):
    template_name = "prazo.html"
    title = "Prazo"

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super(PrazoView, self).get_context_data(**kwargs)
        hoje = timezone.localdate()
        hoje_aware = timezone.make_aware(datetime.combine(hoje, datetime.min.time()))
        eventos = Evento.objects.filter(
            data_inicio__gte=hoje_aware,).filter(
            tipo="prazo",).order_by('data_inicio')[:5]
        context["title"] = self.title
        context["agenda"] = eventos
        return context
