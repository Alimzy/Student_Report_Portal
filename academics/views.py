from rest_framework import viewsets
from .models import Course, AcademicSession
from .serializers import CourseSerializer, AcademicSessionSerializer


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        department_id = self.kwargs.get('departments_pk')
        if department_id:
            return Course.objects.filter(department_id=department_id)
        return Course.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['department_id'] = self.kwargs.get('departments_pk')
        return context


class AcademicsViewSet(viewsets.ModelViewSet):
    queryset = AcademicSession.objects.all()
    serializer_class = AcademicSessionSerializer
