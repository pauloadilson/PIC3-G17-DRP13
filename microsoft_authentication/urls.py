from django.urls import path
from microsoft_authentication.views import CallbackView, SignInView, SignOutView

urlpatterns = [
    path('microsoft_signin', SignInView.as_view(), name='signin'),
    path('microsoft_signout', SignOutView.as_view(), name='signout'),
    path('callback/', CallbackView.as_view(), name='callback'),
]
