from django.urls import include, path
from rest_framework_nested import routers

from academics.views import CourseViewSet

from .views import DepartmentViewSet, health_check

router = routers.DefaultRouter()
router.register("departments", DepartmentViewSet, basename="departments")
dept_router = routers.NestedDefaultRouter(router, "departments")
dept_router.register("course", CourseViewSet, basename="course")


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("", include(router.urls)),
    path("", include(dept_router.urls)),
]
