from rest_framework import permissions
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class ExcludeViewerMixin(UserPassesTestMixin):
    """
    Bloqueia acesso se o usuário pertencer ao grupo 'viewer'.
    """
    def test_func(self):
        # retorna False para usuários do grupo 'viewer'
        return not self.request.user.groups.filter(name='viewer').exists()

    def handle_no_permission(self):
        # opcional: levantar 403 ou redirecionar
        raise PermissionDenied("Você não tem permissão para acessar esta página.")


class GlobalDefaultPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        model_permission_codename = self.__get_model_permission_codename(
            method=request.method,
            view=view,
        )

        if not model_permission_codename:
            return False

        return request.user.has_perm(model_permission_codename)

    def __get_model_permission_codename(self, method, view):
        try:
            model_name = view.queryset.model._meta.model_name
            app_label = view.queryset.model._meta.app_label
            action = self.__get_action_sufix(method)
            return f'{app_label}.{action}_{model_name}'
        except AttributeError:
            return None

    def __get_action_sufix(self, method):
        method_actions = {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete',
            'OPTIONS': 'view',
            'HEAD': 'view',
        }
        return method_actions.get(method, '')