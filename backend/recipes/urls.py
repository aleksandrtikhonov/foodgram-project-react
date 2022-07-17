from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteView, GetShoppingList, IngredientViewSet,
                    RecipeViewSet, ShoppingCartView, TagViewSet)

router = DefaultRouter()

router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes\/(?P<recipe_id>\d+)',
                RecipeViewSet, basename='recipe')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('recipes/<int:recipe_id>/favorite/', FavoriteView.as_view()),
    path('recipes/<int:recipe_id>/shopping_cart/', ShoppingCartView.as_view()),
    path('recipes/download_shopping_cart/', GetShoppingList.as_view()),
    path('', include(router.urls)),
]
