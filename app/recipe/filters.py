from django_filters import rest_framework as filters
from recipe.models import Recipe


class RecipeFilter(filters.FilterSet):
    """FilterSet for Recipe model."""

    category = filters.NumberFilter(field_name='category__id')
    tags = filters.CharFilter(method='filter_tags')
    difficulty = filters.CharFilter(field_name='difficulty')
    max_time = filters.NumberFilter(method='filter_max_time')
    author = filters.NumberFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['category', 'tags', 'difficulty', 'author']

    def filter_tags(self, queryset, name, value):
        """Filter by tags (comma-separated IDs)."""
        if value:
            tag_ids = [int(id.strip()) for id in value.split(',') if id.strip()]
            if tag_ids:
                return queryset.filter(tags__id__in=tag_ids).distinct()
        return queryset

    def filter_max_time(self, queryset, name, value):
        """Filter by maximum total time (prep_time + cook_time)."""
        if value:
            # Filter recipes where total time is less than or equal to max_time
            # Handle null values by treating them as 0
            from django.db.models import F, Value
            from django.db.models.functions import Coalesce

            return queryset.annotate(
                _total_time_calc=Coalesce(F('prep_time'), Value(0)) + Coalesce(F('cook_time'), Value(0))
            ).filter(_total_time_calc__lte=value)
        return queryset
