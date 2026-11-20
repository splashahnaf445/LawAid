from rest_framework import serializers

from .models import Court, PracticeArea


class CourtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Court
        fields = ["id", "name", "court_type", "district"]


class PracticeAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeArea
        fields = ["id", "slug", "name_en", "name_bn"]
