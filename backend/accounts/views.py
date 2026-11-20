from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import ClientRegisterSerializer, LawyerRegisterSerializer, CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """JWT Token endpoint returning tokens and user verification payload."""
    serializer_class = CustomTokenObtainPairSerializer

class CurrentUserView(APIView):
    """Retrieves authenticated user profile and verification status."""
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

class RegisterClientView(APIView):
    """Client registration endpoint (FR-1)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ClientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'status': 'success',
                    'message': 'Client registered successfully.',
                    'user_id': str(user.id),
                    'email': user.email
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterLawyerView(APIView):
    """
    Lawyer Registration with mandatory NID and Bar Council Certificate upload.
    Uploaded documents are immediately encrypted at rest using AES-128-CBC + HMAC.
    SRS: FR-1, FR-2, NFR-1, NFR-4.
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LawyerRegisterSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
            return Response(
                {
                    'status': 'success',
                    'message': 'Lawyer registration submitted successfully. Your NID and Bar Council certificate have been securely encrypted and queued for administrator verification.',
                    'lawyer_id': str(profile.user.id),
                    'email': profile.user.email,
                    'bar_council_no': profile.bar_council_no,
                    'verification_status': profile.verification_status,
                    'is_verified': profile.is_verified,
                    'badge': profile.get_verification_badge(),
                    'notice': 'Your profile will remain hidden from client search results until verification is approved by a platform administrator (SRS FR-3).'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
