from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
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
from cpprev.permissions import GlobalDefaultPermission
from microsoft_authentication.graph_helper import criar_evento_no_microsoft_graph
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pytz
from microsoft_authentication.auth_helper import get_token
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from agenda.serializers import EventoSerializer
from django.core.cache import cache


@method_decorator(login_required(login_url='login'), name='dispatch')
class AgendaView(ListView):
    model = Evento
    template_name = 'agenda.html'
    context_object_name = 'agenda'
    title = "Agenda"
    paginate_by = 10

    def get_queryset(self):
        cache_key = f"agenda_de_eventos_{'_'.join(ordering)}"

        eventos = cache.get(cache_key)
        if eventos is None:
            print("--- CACHE MISS --- Buscando do banco e salvando no Redis.")
            eventos = Evento.objects.all()
            TIMEOUT = 900
            cache.set(cache_key, eventos, TIMEOUT)
        else:
            print("--- CACHE HIT --- Servindo lista de eventos diretamente do Redis!")

        return eventos

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
        # salva o objeto em memória sem gravar no banco ainda
        self.object = form.save(commit=False)

        # se data_fim estiver em branco, define +30 minutos a partir de data_inicio
        if not self.object.data_fim and self.object.data_inicio:
            self.object.data_fim = self.object.data_inicio + timedelta(hours=1)

        # salva no banco de dados
        self.object.save()

        # depois chama o restante do comportamento padrão da CreateView
        response = super().form_valid(form)

        # tenta criar o evento no Microsoft Graph
        try:
            criar_evento_no_microsoft_graph(self.request, self.object)
            messages.success(self.request, 'Evento criado e sincronizado com o calendário do Microsoft Outlook.')
        except Exception:
            messages.error(self.request, 'Erro ao criar evento no Microsoft Calendar! '
                                         'Realize a inclusão manualmente no Microsoft Outlook.')
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


class EventoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, GlobalDefaultPermission)
    serializer_class = EventoSerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventoSerializer
        return super().get_serializer_class()

    def get_ordering(self):
        """Dynamic ordering based on request parameters"""
        ordering = self.request.GET.get('ordering', '-data_inicio')
        return ordering.split(',') if ordering else ['-data_inicio']

    def get_queryset(self):
        """Return a list of eventos, filtering by is_deleted=False."""
        ordering = self.get_ordering()
        base_queryset = Evento.objects.order_by(*ordering)
        
        # Cache logic ONLY for list view
        if self.action == 'list':
            cache_key = f"lista_de_eventos_api_{'_'.join(ordering)}"
            eventos = cache.get(cache_key)

            if eventos is None:
                print(f"--- API CACHE MISS ({cache_key}) --- Buscando do banco e salvando no Redis.")
                eventos = base_queryset
                TIMEOUT = 900
                cache.set(cache_key, eventos, TIMEOUT)
            else:
                print(f"--- API CACHE HIT ({cache_key}) --- Recuperando do Redis.")
        
        return eventos
