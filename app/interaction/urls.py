from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interaction import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')

app_name = 'interaction'

urlpatterns = [
    path('', include(router.urls)),
]
