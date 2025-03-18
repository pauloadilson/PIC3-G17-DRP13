from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('authentication/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
]