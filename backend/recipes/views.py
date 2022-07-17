from django.shortcuts import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import IngredientNameSearchFilter, RecipeFilter
from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, User)
from .permissions import IsAuthorOrReadOnly
from .serializers import (IngredientSerializer, MiniRecipe,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [IsAuthorOrReadOnly, ]
    queryset = Ingredient.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_fields = ['name', ]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthorOrReadOnly, ]
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [IsAuthorOrReadOnly, ]
    pagination_class = None


class FavoriteView(APIView):
    permission_classes = [IsAuthorOrReadOnly, ]

    def post(self, request, recipe_id):
        user = User.objects.get(username=request.user.username)
        recipe = Recipe.objects.get(pk=recipe_id)
        if FavoriteRecipes.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {
                    'error': 'Рецепт уже в избранном'
                }, status=status.HTTP_400_BAD_REQUEST
            )
        FavoriteRecipes.objects.create(user=user, recipe=recipe)
        serializer = MiniRecipe(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = User.objects.get(username=request.user.username)
        recipe = Recipe.objects.get(pk=recipe_id)
        favorite = FavoriteRecipes.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепт в списке избранных не найден'},
            status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request, recipe_id):
        user = User.objects.get(username=request.user.username)
        recipe = Recipe.objects.get(pk=recipe_id)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {'error': 'Рецепт уже в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = MiniRecipe(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = User.objects.get(username=request.user.username)
        recipe = Recipe.objects.get(pk=recipe_id)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Рецепт в списке покупок не найден'},
            status=status.HTTP_400_BAD_REQUEST)


class GetShoppingList(APIView):
    def get(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__carts_recipe__user=request.user)
        shop_list = {}
        for ingredient in ingredients:
            ingredient_name = ingredient.ingredient.name
            ingredient_measurement_unit = (
                ingredient.ingredient.measurement_unit
            )
            ingredient_amount = ingredient.amount
            if ingredient_name not in shop_list.keys():
                shop_list[ingredient_name] = {
                    'measurement_unit': ingredient_measurement_unit,
                    'amount': ingredient_amount
                }
            else:
                shop_list[ingredient_name]['amount'] += ingredient_amount
        shoping_list = ''
        for key, value in shop_list.items():
            measurement_unit = shop_list[key].get('measurement_unit')
            amount = shop_list[key].get('amount')
            shoping_list += f'{key} ({measurement_unit}) - {amount}\n'
        response = HttpResponse(shoping_list, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shoping_list.txt"'
        )
        return response
