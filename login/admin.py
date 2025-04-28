from django.contrib import admin
from django.contrib.sessions.models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'expire_date', 'session_data')
    search_fields = ('session_key', 'session_data')
    list_filter = ('expire_date',)
