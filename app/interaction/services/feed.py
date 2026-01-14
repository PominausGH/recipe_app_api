from interaction.models import Follow, Mute, FeedPreference, Rating, Favorite
from recipe.models import Recipe


class FeedService:
    """Service for generating activity feeds."""

    @classmethod
    def get_feed(cls, user, order='chronological', limit=50):
        """Get activity feed for a user."""
        # Get users this user follows
        following_ids = Follow.objects.filter(
            follower=user
        ).values_list('following_id', flat=True)

        # Exclude muted users
        muted_ids = Mute.objects.filter(
            user=user
        ).values_list('muted_user_id', flat=True)

        active_following_ids = [
            uid for uid in following_ids if uid not in muted_ids
        ]

        # Get user preferences
        try:
            prefs = user.feed_preferences
        except FeedPreference.DoesNotExist:
            prefs = None

        feed_items = []

        # Get recipes
        if prefs is None or prefs.show_recipes:
            recipes = Recipe.objects.filter(
                author_id__in=active_following_ids,
                is_published=True,
            ).select_related('author').order_by('-created_at')[:limit]

            for recipe in recipes:
                feed_items.append({
                    'type': 'recipe',
                    'actor': recipe.author,
                    'recipe': recipe,
                    'created_at': recipe.created_at,
                })

        # Get ratings
        if prefs is None or prefs.show_ratings:
            ratings = Rating.objects.filter(
                user_id__in=active_following_ids,
            ).select_related('user', 'recipe').order_by('-created_at')[:limit]

            for rating in ratings:
                feed_items.append({
                    'type': 'rating',
                    'actor': rating.user,
                    'recipe': rating.recipe,
                    'score': rating.score,
                    'created_at': rating.created_at,
                })

        # Get favorites
        if prefs and prefs.show_favorites:
            favorites = Favorite.objects.filter(
                user_id__in=active_following_ids,
            ).select_related('user', 'recipe').order_by('-created_at')[:limit]

            for favorite in favorites:
                feed_items.append({
                    'type': 'favorite',
                    'actor': favorite.user,
                    'recipe': favorite.recipe,
                    'created_at': favorite.created_at,
                })

        # Sort by date
        if order == 'chronological':
            feed_items.sort(key=lambda x: x['created_at'], reverse=True)

        return feed_items[:limit]
