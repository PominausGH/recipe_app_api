from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db import models

from recipe.models import Recipe
from recipe.serializers import (
    RecipeListSerializer,
    RecipeDetailSerializer,
    RecipeCreateSerializer,
)
from recipe.permissions import IsOwnerOrReadOnly
from interaction.models import Rating, Favorite, Comment
from interaction.serializers import (
    RatingSerializer,
    RatingCreateSerializer,
    FavoriteSerializer,
    CommentSerializer,
    CommentCreateSerializer,
)


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
        if self.action == 'rate':
            return RatingCreateSerializer
        if self.action == 'comments':
            if self.request.method == 'POST':
                return CommentCreateSerializer
            return CommentSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        """Rate a recipe or update existing rating."""
        recipe = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating, created = Rating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults=serializer.validated_data,
        )

        output_serializer = RatingSerializer(rating)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(output_serializer.data, status=status_code)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Toggle favorite status for a recipe."""
        recipe = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )

        if not created:
            favorite.delete()
            return Response(
                {'status': 'removed from favorites'},
                status=status.HTTP_200_OK,
            )

        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """List or create comments for a recipe."""
        recipe = self.get_object()

        if request.method == 'GET':
            comments = Comment.objects.filter(recipe=recipe, parent=None)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        # POST - requires authentication
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={'recipe_id': recipe.id},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
