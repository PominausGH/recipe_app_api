from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipe.urls')),
    path('api/', include('interaction.urls')),
    path('api/auth/', include('core.urls')),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='api-schema'),
        name='api-docs',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='api-schema'),
        name='api-redoc',
    ),
]
