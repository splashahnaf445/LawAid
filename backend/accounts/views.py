from rest_framework import generics, permissions
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import ClientRegisterSerializer, CustomTokenObtainPairSerializer, LawyerRegisterSerializer


class _RegisterView(generics.CreateAPIView):
    """
    Usama (SYS-18): public, throttled (settings: DEFAULT_THROTTLE_RATES['register']).
    Returns 201 + the new account.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"


class RegisterClientView(_RegisterView):
    """Client registration endpoint (FR-1)."""
    serializer_class = ClientRegisterSerializer


class RegisterLawyerView(_RegisterView):
    """
    Lawyer registration (FR-1) with mandatory NID and Bar Council certificate upload (FR-2).
    Uploaded documents are encrypted at rest (NFR-1, NFR-4). Multipart is required for the files.
    """
    serializer_class = LawyerRegisterSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]


class CustomTokenObtainPairView(TokenObtainPairView):
    """Ahnaf (SYS-21/22): JWT token endpoint returning tokens and user verification payload."""
    serializer_class = CustomTokenObtainPairSerializer


class CurrentUserView(APIView):
    """Ahnaf (SYS-21/22): authenticated user profile and verification status."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        user_info = {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'phone': user.phone,
            'status': user.status,
            'is_admin': user.is_admin,
        }
        if hasattr(user, 'lawyer_profile'):
            lp = user.lawyer_profile
            user_info['verification_status'] = lp.verification_status
            user_info['is_verified'] = lp.is_verified
            user_info['bar_council_no'] = lp.bar_council_no
            user_info['badge'] = lp.get_verification_badge()
        return Response(user_info)
