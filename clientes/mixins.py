from django.http import Http404


class SoftDeleteGetMixin:
    """
    Mixin para sobrescrever get_object e impedir o acesso a itens
    que foram marcados como deletados (soft-delete).
    """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Usamos getattr para não quebrar se o modelo não tiver 'is_deleted'
        if getattr(obj, 'is_deleted', False):
            raise Http404(f"{self.model._meta.verbose_name.capitalize()} não encontrado")
        return obj

