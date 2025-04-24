from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from cpprev_authentication.views import UserInfoView

urlpatterns = [
    path('authentication/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
]
