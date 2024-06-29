from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer


# class UserProfileView(generics.RetrieveAPIView):
#     serializer_class = UserSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_object(self):
#         return self.request.user
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": str(e)}, status=500)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if user.is_staff:
                    return JsonResponse({"redirect": "teacher.html"})
                else:
                    return JsonResponse({"redirect": "student.html"})
            else:
                return Response({"detail": "Аккаунт отключен."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_400_BAD_REQUEST)
