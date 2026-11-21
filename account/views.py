import logging

from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.constants import ROLE_STAFF, ROLE_STUDENT
from core.models import Department, User

from .models import Staff, Student
from .serializer import (
    LoginSerializer,
    LogoutSerializer,
    StaffEnrollmentSerializer,
    StudentEnrollmentSerializer,
)

logger = logging.getLogger(__name__)


class StudentEnrollment(APIView):
    """Legacy enrollment endpoint. Kept working until the Batch 2 domain swap."""

    serializer_class = StudentEnrollmentSerializer

    def post(self, request, *args, **kwargs):
        serializer = StudentEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            department = Department.objects.get(
                department_code=serializer.validated_data["department_code"]
            )
            with transaction.atomic():
                user = User.objects.create_user(
                    email=serializer.validated_data["email"],
                    username=serializer.validated_data["username"],
                    password=serializer.validated_data["password"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    role=ROLE_STUDENT,
                )
                student = Student.objects.create(
                    user=user,
                    department=department,
                    entry_year=serializer.validated_data["entry_year"],
                )
        except Department.DoesNotExist:
            return Response(
                {"detail": "Unknown department code."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            logger.warning("Student enrollment failed due to a database conflict.")
            return Response(
                {"detail": "A student with these details already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": user.id,
                "matric_number": student.matric_number,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class StaffEnrollment(APIView):
    """Legacy staff enrollment endpoint. Kept working until the Batch 2 swap."""

    serializer_class = StaffEnrollmentSerializer

    def post(self, request, *args, **kwargs):
        serializer = StaffEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            department = Department.objects.get(
                department_code=serializer.validated_data["department_code"]
            )
            with transaction.atomic():
                user = User.objects.create_user(
                    email=serializer.validated_data["email"],
                    username=serializer.validated_data["username"],
                    password=serializer.validated_data["password"],
                    first_name=serializer.validated_data["first_name"],
                    last_name=serializer.validated_data["last_name"],
                    role=ROLE_STAFF,
                )
                staff = Staff.objects.create(user=user, department=department)
        except Department.DoesNotExist:
            return Response(
                {"detail": "Unknown department code."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            logger.warning("Staff enrollment failed due to a database conflict.")
            return Response(
                {"detail": "A staff member with these details already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "id": user.id,
                "staff_id": staff.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Throttled email/password login returning access and refresh tokens."""

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            logger.info("Successful login")
        else:
            client_ip = request.META.get("REMOTE_ADDR", "unknown")
            logger.warning("Failed login attempt from %s", client_ip)
        return response


class RefreshView(TokenRefreshView):
    """Rotate a refresh token and return a fresh access token."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh"


class LogoutView(APIView):
    """Blacklist the supplied refresh token."""

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)
