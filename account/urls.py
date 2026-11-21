from django.urls import path

from . import views

urlpatterns = [
    path("student-enroll/", views.StudentEnrollment.as_view(), name="student-enrollment"),
    path("staff-enroll/", views.StaffEnrollment.as_view(), name="staff-enrollment"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/refresh/", views.RefreshView.as_view(), name="token-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
]
