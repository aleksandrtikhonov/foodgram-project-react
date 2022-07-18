from django_filters import CharFilter, FilterSet, NumberFilter
from rest_framework.filters import SearchFilter

from .models import Recipe


class IngredientNameSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):

    author = CharFilter(field_name='author__id', lookup_expr='iexact')
    tags = CharFilter(field_name='tags__slug', lookup_expr='iexact')
    is_favorited = NumberFilter(
        field_name='is_favorited', method='get_is_favorited'
    )
    is_in_shopping_cart = NumberFilter(
        field_name='is_in_shopping_cart', method='get_is_in_shopping_cart'
    )
    recipes_limit = NumberFilter(
        field_name='recipes_limit', method='get_recipes_limit'
    )

    def get_is_favorited(self, queryset, name, value):
        if value == 1 and not self.request.user.is_anonymous:
            return queryset.filter(favorites_recipe__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == 1 and not self.request.user.is_anonymous:
            return queryset.filter(carts_recipe__user=self.request.user)
        return queryset

    def get_recipes_limit(self, queryset, name, value):
        print(queryset)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
            'recipes_limit'
        )
