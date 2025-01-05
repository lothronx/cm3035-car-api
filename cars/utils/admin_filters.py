from django.contrib import admin
from django.db.models import Prefetch
from cars.models import TagCategory, Tag


class TagFilter(admin.SimpleListFilter):
    """Filter for cars based on their associated tags, grouped by tag categories."""
    
    title = "Tags"
    parameter_name = "tag"

    def lookups(self, request, model_admin):
        # Get all categories with their tags in a single query
        categories = TagCategory.objects.prefetch_related(
            Prefetch(
                'tag_set',
                queryset=Tag.objects.order_by('value')
            )
        ).order_by('name')
        
        choices = []
        for category in categories:
            # Add category name as a header
            choices.append((f"__category__{category.name}", f"=={category.name}=="))
            # Add all tags in this category (already prefetched)
            choices.extend([(str(tag.id), f"{tag.value}") for tag in category.tag_set.all()])
        return choices

    def queryset(self, request, queryset):
        if not self.value() or self.value().startswith("__category__"):
            return queryset
        return queryset.filter(tag__id=self.value())
