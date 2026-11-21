#
# from .views import create_course
# from django.urls import path
#
#
# urlpatterns = [
# path('create_course/', create_course, name='create_course'),
#     ]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AcademicsViewSet

router = DefaultRouter()
router.register('academics', AcademicsViewSet, basename='academics')

urlpatterns = [
    path('', include(router.urls)),
]
