# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print()
        return Response({
            'username': request.user.username,
            'role': request.user.groups.first().name if request.user.groups.exists() else 'user'
        })
