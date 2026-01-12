from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from recipe.models import Recipe
from recipe.serializers import (
    RecipeListSerializer,
    RecipeDetailSerializer,
    RecipeCreateSerializer,
)
from recipe.permissions import IsOwnerOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipes."""
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        """Return recipes based on user authentication."""
        if self.request.user.is_authenticated:
            return Recipe.objects.filter(
                models.Q(author=self.request.user) |
                models.Q(is_published=True)
            ).distinct()
        return Recipe.objects.filter(is_published=True)

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return RecipeListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(author=self.request.user)
