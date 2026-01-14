from django.urls import include, path
from interaction import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("users", views.UserViewSet, basename="user")
router.register("notifications", views.NotificationViewSet, basename="notification")
router.register("feed", views.FeedViewSet, basename="feed")

app_name = "interaction"

urlpatterns = [
    path("", include(router.urls)),
]
