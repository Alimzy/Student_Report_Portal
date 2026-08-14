from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User, Department


class StudentEnrollmentSerializer(serializers.Serializer):
    department_code = serializers.CharField(max_length=10, required=True)
    entry_year = serializers.IntegerField()
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

class StaffEnrollmentSerializer(serializers.Serializer):
    department_code = serializers.CharField(max_length=10, required=True)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    #
    #
    # {
    #     "department": "ENG",
    #     "entry_year": 2024,
    #     "email": "salamialameen20@gmail.com",
    #     "username": "Alimzy",
    #     "password": "Alimzy-01",
    #     "first_name": "Salami",
    #     "last_name": "Al-Ameen"
    #
    # }

class CustomTokenObtainSerializer(TokenObtainSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        refresh = RefreshToken.for_user(user)

        data["user"] = {
            "id": user.id,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": user.email,
            "username": user.username,
            "role": user.role
        }

        return data