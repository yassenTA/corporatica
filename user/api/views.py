from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from user.api.serializer import RegisterSerializer, LoginSerializer

# Assuming RegisterSerializer and LoginSerializer are defined elsewhere
class RegisterView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
