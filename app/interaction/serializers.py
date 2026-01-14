from interaction.models import (
    Block,
    Comment,
    Favorite,
    Follow,
    FollowRequest,
    Mute,
    Notification,
    Rating,
)
from recipe.serializers import RecipeListSerializer
from rest_framework import serializers


class RatingSerializer(serializers.ModelSerializer):
    """Serializer for ratings."""

    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Rating
        fields = ["id", "user", "user_email", "score", "review", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class RatingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ratings."""

    class Meta:
        model = Rating
        fields = ["score", "review"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Score must be between 1 and 5.")
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for favorites."""

    class Meta:
        model = Favorite
        fields = ["id", "user", "recipe", "created_at"]
        read_only_fields = ["id", "user", "recipe", "created_at"]


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""

    user_email = serializers.CharField(source="user.email", read_only=True)
    user_name = serializers.CharField(source="user.name", read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "text",
            "parent",
            "replies",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def get_replies(self, obj):
        """Get nested replies for a comment."""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""

    class Meta:
        model = Comment
        fields = ["id", "text", "parent"]
        read_only_fields = ["id"]

    def validate_parent(self, value):
        """Ensure parent comment belongs to the same recipe."""
        if value:
            recipe_id = self.context.get("recipe_id")
            if value.recipe_id != recipe_id:
                raise serializers.ValidationError(
                    "Parent comment must belong to the same recipe."
                )
        return value


class UserSummarySerializer(serializers.Serializer):
    """Lightweight user serializer for social features."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    profile_photo = serializers.ImageField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)


class UserProfileSerializer(serializers.Serializer):
    """Detailed user serializer for profile pages."""

    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    bio = serializers.CharField(read_only=True, allow_null=True)
    profile_photo = serializers.ImageField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    is_private = serializers.BooleanField(read_only=True)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    is_following = serializers.BooleanField(read_only=True)
    has_pending_request = serializers.BooleanField(read_only=True)


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships."""

    follower = UserSummarySerializer(read_only=True)
    following = UserSummarySerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "created_at"]
        read_only_fields = ["id", "follower", "following", "created_at"]


class FollowRequestSerializer(serializers.ModelSerializer):
    """Serializer for follow requests."""

    requester = UserSummarySerializer(read_only=True)
    target = UserSummarySerializer(read_only=True)

    class Meta:
        model = FollowRequest
        fields = ["id", "requester", "target", "status", "created_at"]
        read_only_fields = ["id", "requester", "target", "created_at"]


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for blocks."""

    blocked_user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Block
        fields = ["id", "blocked_user", "created_at"]
        read_only_fields = ["id", "created_at"]


class MuteSerializer(serializers.ModelSerializer):
    """Serializer for mutes."""

    muted_user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Mute
        fields = ["id", "muted_user", "created_at"]
        read_only_fields = ["id", "created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""

    actor = UserSummarySerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "actor",
            "verb",
            "target_type",
            "target_id",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "actor",
            "verb",
            "target_type",
            "target_id",
            "created_at",
        ]


class FeedItemSerializer(serializers.Serializer):
    """Serializer for feed items."""

    type = serializers.CharField()
    actor = UserSummarySerializer()
    recipe = RecipeListSerializer()
    score = serializers.IntegerField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
