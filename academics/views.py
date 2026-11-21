from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import viewsets

from .models import AcademicSession, Course
from .serializers import AcademicSessionSerializer, CourseSerializer

_DEPARTMENT_CODE_PARAM = OpenApiParameter(
    name="nested_1_pk",
    type=str,
    location=OpenApiParameter.PATH,
    description="Department code that owns the course.",
)


@extend_schema_view(
    list=extend_schema(parameters=[_DEPARTMENT_CODE_PARAM]),
    create=extend_schema(parameters=[_DEPARTMENT_CODE_PARAM]),
    retrieve=extend_schema(parameters=[_DEPARTMENT_CODE_PARAM]),
    update=extend_schema(parameters=[_DEPARTMENT_CODE_PARAM]),
    partial_update=extend_schema(parameters=[_DEPARTMENT_CODE_PARAM]),
    destroy=extend_schema(parameters=[_DEPARTMENT_CODE_PARAM]),
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    lookup_field = "course_code"

    def get_queryset(self):
        department_id = self.kwargs.get("nested_1_pk")
        if department_id:
            return Course.objects.filter(department_id=department_id)
        return Course.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["department_id"] = self.kwargs.get("nested_1_pk")
        return context


class AcademicsViewSet(viewsets.ModelViewSet):
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
