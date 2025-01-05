from django.contrib import admin
from .models import TagCategory, Tag


class TagFilter(admin.SimpleListFilter):
    """Filter for cars based on their associated tags, grouped by tag categories."""

    title = "Tags"
    parameter_name = "tag"

    def lookups(self, request, model_admin):
        # Get all unique tag categories and their values
        categories = TagCategory.objects.all()
        choices = []
        for category in categories:
            # Add category name as a header
            choices.append((f"__category__{category.name}", f"=={category.name}=="))
            # Add all tags in this category
            tags = Tag.objects.filter(category=category)
            choices.extend([(str(tag.id), f"{tag.value}") for tag in tags])
        return choices

    def queryset(self, request, queryset):
        if not self.value() or self.value().startswith("__category__"):
            return queryset
        return queryset.filter(tag__id=self.value())
