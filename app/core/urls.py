from core import views
from django.urls import path

app_name = "auth"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomTokenObtainPairView.as_view(), name="login"),
    path("refresh/", views.CustomTokenRefreshView.as_view(), name="refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        views.ResendVerificationView.as_view(),
        name="resend-verification",
    ),
]
