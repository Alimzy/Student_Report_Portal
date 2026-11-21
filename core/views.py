from django.db import connection
from django.utils import timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Department
from .serializers import DepartmentSerializer


@extend_schema(
    tags=["system"],
    summary="Service health check",
    description="Public liveness/readiness probe used by Docker and hosting platforms.",
    responses={
        200: OpenApiResponse(description="Service and database are healthy."),
        503: OpenApiResponse(description="Service is up but the database is unavailable."),
    },
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    """Return service status without exposing configuration details."""
    database_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # pragma: no cover - depends on external database state
        database_ok = False

    payload = {
        "status": "ok" if database_ok else "degraded",
        "database": "ok" if database_ok else "unavailable",
        "version": "1.0.0",
        "timestamp": timezone.now().isoformat(),
    }
    http_status = status.HTTP_200_OK if database_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(payload, status=http_status)


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    search_fields = ["name", "department_code"]
    ordering_fields = ["name", "department_code", "created_at"]
