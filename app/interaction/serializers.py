from rest_framework import serializers
from interaction.models import Rating, Favorite, Comment


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'user_email', 'score', 'review', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class RatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ratings."""

    class Meta:
        model = Rating
        fields = ['score', 'review']

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Score must be between 1 and 5.')
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorites."""

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'recipe', 'created_at']
        read_only_fields = ['id', 'user', 'recipe', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'user_email', 'user_name',
            'text', 'parent', 'replies', 'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def get_replies(self, obj):
        """Get nested replies for a comment."""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""

    class Meta:
        model = Comment
        fields = ['id', 'text', 'parent']
        read_only_fields = ['id']

    def validate_parent(self, value):
        """Ensure parent comment belongs to the same recipe."""
        if value:
            recipe_id = self.context.get('recipe_id')
            if value.recipe_id != recipe_id:
                raise serializers.ValidationError(
                    'Parent comment must belong to the same recipe.'
                )
        return value
