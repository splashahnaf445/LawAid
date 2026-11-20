from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import Court, PracticeArea
from .serializers import CourtSerializer, PracticeAreaSerializer


class _PublicList(ListAPIView):
    """Reference data for the registration dropdowns - public, unpaginated."""

    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None


class CourtListView(_PublicList):
    queryset = Court.objects.all()
    serializer_class = CourtSerializer


class PracticeAreaListView(_PublicList):
    queryset = PracticeArea.objects.all()
    serializer_class = PracticeAreaSerializer
