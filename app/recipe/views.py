import re

from core.throttling import RecipeCreateThrottle
from django.db import models
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from interaction.models import Comment, Favorite, Rating
from interaction.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    FavoriteSerializer,
    RatingCreateSerializer,
    RatingSerializer,
)
from recipe.filters import RecipeFilter
from recipe.models import Recipe
from recipe.permissions import IsOwnerOrReadOnly
from recipe.serializers import (
    RecipeCreateSerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
)
from recipe_scrapers import scrape_me
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipes."""

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    throttle_classes = [RecipeCreateThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecipeFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "prep_time", "cook_time", "avg_rating"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return recipes based on user authentication."""
        queryset = Recipe.objects.annotate(avg_rating=Avg("ratings__score"))

        if self.request.user.is_authenticated:
            return queryset.filter(
                models.Q(author=self.request.user) | models.Q(is_published=True)
            ).distinct()
        return queryset.filter(is_published=True)

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == "list":
            return RecipeListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return RecipeCreateSerializer
        if self.action == "rate":
            return RatingCreateSerializer
        if self.action == "comments":
            if self.request.method == "POST":
                return CommentCreateSerializer
            return CommentSerializer
        if self.action == "upload_image":
            from recipe.serializers_image import RecipeImageSerializer

            return RecipeImageSerializer
        return RecipeDetailSerializer

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
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
        if created:
            status_code = status.HTTP_201_CREATED
        else:
            status_code = status.HTTP_200_OK
        return Response(output_serializer.data, status=status_code)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
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
                {"status": "removed from favorites"},
                status=status.HTTP_200_OK,
            )

        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["get", "post"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def comments(self, request, pk=None):
        """List or create comments for a recipe."""
        recipe = self.get_object()

        if request.method == "GET":
            comments = Comment.objects.filter(recipe=recipe, parent=None)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        # POST - requires authentication
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(
            data=request.data,
            context={"recipe_id": recipe.id},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsOwnerOrReadOnly],
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            # Process the image before saving
            image = request.FILES.get("image")
            if image:
                from core.utils import process_image, validate_image

                is_valid, error = validate_image(image)
                if not is_valid:
                    return Response(
                        {"image": [error]},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                processed_image = process_image(image)
                serializer.save(image=processed_image)
            else:
                serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="import-url",
    )
    def import_url(self, request):
        """Import a recipe from a URL."""
        url = request.data.get("url")

        if not url:
            return Response(
                {"url": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            return Response(
                {"url": ["Enter a valid URL."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            scraper = scrape_me(url)

            # Extract data from scraper
            title = scraper.title() or "Imported Recipe"
            description = scraper.description() or ""
            instructions = scraper.instructions() or ""

            # Parse times
            prep_time = scraper.prep_time()
            cook_time = scraper.cook_time()

            # If only total_time is available, use it as cook_time
            if not prep_time and not cook_time:
                total = scraper.total_time()
                if total:
                    cook_time = total

            # Parse servings from yields (e.g., "6 servings" -> 6)
            servings = 1
            yields = scraper.yields()
            if yields:
                match = re.search(r"(\d+)", str(yields))
                if match:
                    servings = int(match.group(1))

            # Create recipe
            recipe = Recipe.objects.create(
                author=request.user,
                title=title,
                description=description,
                instructions=instructions,
                prep_time=prep_time,
                cook_time=cook_time,
                servings=servings,
                source_url=url,
                is_published=False,  # Draft by default
            )

            # Return the created recipe
            serializer = RecipeDetailSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            error_msg = str(e)
            if "not implemented" in error_msg.lower():
                error_msg = "This website is not supported for recipe import."
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )
