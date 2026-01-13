from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('recipe.urls')),
    path('api/', include('interaction.urls')),
    path('api/auth/', include('core.urls')),
]
