from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle

from .serializers import ClientRegisterSerializer, LawyerRegisterSerializer


class _RegisterView(generics.CreateAPIView):
    """Public, throttled (settings: DEFAULT_THROTTLE_RATES['register']). Returns 201 + the new account."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"


class RegisterClientView(_RegisterView):
    serializer_class = ClientRegisterSerializer


class RegisterLawyerView(_RegisterView):
    serializer_class = LawyerRegisterSerializer
