from rest_framework import serializers
from recipe.models import Recipe, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'quantity', 'unit', 'order']


class RecipeListSerializer(serializers.ModelSerializer):
    """Serializer for recipe list view."""
    author_name = serializers.CharField(source='author.name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'author', 'author_name',
            'prep_time', 'cook_time', 'total_time', 'servings',
            'difficulty', 'image', 'created_at', 'average_rating',
            'rating_count',
        ]
        read_only_fields = ['id', 'author', 'created_at']


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for recipe detail view."""
    ingredients = IngredientSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'author',
            'author_name', 'prep_time', 'cook_time', 'total_time',
            'servings', 'difficulty', 'image', 'is_published',
            'category', 'tags', 'ingredients', 'created_at', 'updated_at',
            'average_rating', 'rating_count',
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating recipes."""
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions',
            'prep_time', 'cook_time', 'servings', 'difficulty',
            'is_published', 'category', 'tags', 'ingredients',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        for idx, ingredient_data in enumerate(ingredients_data):
            ingredient_data['order'] = idx
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags is not None:
            instance.tags.set(tags)

        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for idx, ingredient_data in enumerate(ingredients_data):
                ingredient_data['order'] = idx
                Ingredient.objects.create(recipe=instance, **ingredient_data)

        return instance
