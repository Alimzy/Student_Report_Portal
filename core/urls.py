from .views import create_department
from django.urls import path

urlpatterns = [
    path( 'create_department/', create_department, name='create_department'),
]