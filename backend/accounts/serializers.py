from rest_framework import serializers

from .models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(trim_whitespace=False, write_only=True)
    remember = serializers.BooleanField(required=False, default=True)      
    portal = serializers.ChoiceField(choices=["client", "lawyer", "admin"], required=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "email", "role", "avatar_url", "preferred_language", "two_factor_enabled"]
