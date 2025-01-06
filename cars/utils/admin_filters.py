"""
Utility functions and filters for Django admin interface.
This module provides filtering functionality for the car admin interface,
specifically for filtering cars by their tags.
"""

from django.contrib import admin
from django.db.models import Prefetch, QuerySet
from cars.models import TagCategory, Tag
from typing import List, Tuple, Optional


def get_tag_categories() -> QuerySet:
    """
    Fetch all tag categories with their associated tags in a single optimized query.
    
    Returns:
        QuerySet: Tag categories with prefetched tags, ordered by name
    """
    return TagCategory.objects.prefetch_related(
        Prefetch(
            'tag_set',
            queryset=Tag.objects.order_by('value')
        )
    ).order_by('name')


def format_category_choice(category_name: str) -> Tuple[str, str]:
    """
    Format a category name into a choice tuple for the admin filter.
    
    Args:
        category_name: Name of the tag category
        
    Returns:
        Tuple containing the category identifier and display name
    """
    return (f"__category__{category_name}", f"=={category_name}==")


def format_tag_choice(tag: Tag) -> Tuple[str, str]:
    """
    Format a tag into a choice tuple for the admin filter.
    
    Args:
        tag: Tag instance to format
        
    Returns:
        Tuple containing the tag ID and display value
    """
    return (str(tag.id), tag.value)


def get_filter_choices() -> List[Tuple[str, str]]:
    """
    Generate the complete list of choices for the tag filter.
    
    Returns:
        List of tuples containing filter choices, including category headers
        and their associated tags
    """
    choices = []
    categories = get_tag_categories()
    
    for category in categories:
        choices.append(format_category_choice(category.name))
        choices.extend([format_tag_choice(tag) for tag in category.tag_set.all()])
    
    return choices


def filter_queryset_by_tag(queryset: QuerySet, tag_id: str) -> QuerySet:
    """
    Filter the queryset based on the selected tag ID.
    
    Args:
        queryset: Base queryset to filter
        tag_id: Selected tag ID from the filter
        
    Returns:
        Filtered queryset if a valid tag is selected, otherwise returns
        the original queryset
    """
    if not tag_id or tag_id.startswith("__category__"):
        return queryset
    return queryset.filter(tag__id=tag_id)


class TagFilter(admin.SimpleListFilter):
    """
    Admin filter for cars based on their associated tags.
    Tags are grouped by categories for better organization.
    """
    
    title = "Tags"
    parameter_name = "tag"

    def lookups(self, request, model_admin) -> List[Tuple[str, str]]:
        """Get all possible filter options."""
        return get_filter_choices()

    def queryset(self, request, queryset) -> QuerySet:
        """Apply the selected filter to the queryset."""
        return filter_queryset_by_tag(queryset, self.value())