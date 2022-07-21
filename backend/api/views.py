from django.contrib.auth import get_user_model
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (FavoriteRecipes, Ingredient, Recipe, ShoppingCart,
                            Tag)
from recipes.utils import make_shopping_cart
from users.models import Follow

from .filters import IngredientNameSearchFilter, RecipeFilter
from .permissions import IsAuthorOrStaffOrReadOnly
from .serializers import (AddToFavoriteSerializer,
                          CurrentUserSubscriptionsSeriazlizer,
                          IngredientSerializer, ManageSubscribeSerializer,
                          MiniRecipe, RecipeReadSerializer,
                          RecipeWriteSerializer, TagSerializer, UserSerializer)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        AllowAny,
    ]


class ManageSubscribeView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user

        if author == follower:
            return Response(
                {"error": "Нельзя подписываться на самого себя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(user=follower, author=author).exists():
            return Response(
                {"error": "Вы уже подписаны на данного пользователя"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Follow.objects.create(user=follower, author=author)
        serializer = ManageSubscribeSerializer(author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        author = get_object_or_404(User, id=user_id)
        follower = request.user

        follow = Follow.objects.filter(user=follower, author=author)
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Подписка не найдена"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def get(self, request, user_id):
        profile = get_object_or_404(User, id=user_id)
        serializer = UserSerializer(profile, context={"request": request})
        return Response(serializer.data)


class CurrentUserSubscriptionsView(ListAPIView):
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = PageNumberPagination
    serializer_class = CurrentUserSubscriptionsSeriazlizer
    allowed_methods = [
        "GET",
    ]

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = [
        IsAuthorOrStaffOrReadOnly,
    ]
    queryset = Ingredient.objects.all()
    filter_backends = (IngredientNameSearchFilter,)
    search_fields = ("^name",)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthorOrStaffOrReadOnly,
    ]
    queryset = Recipe.objects.all()
    filter_backends = [
        DjangoFilterBackend,
    ]
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return RecipeReadSerializer
        return RecipeWriteSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [
        IsAuthorOrStaffOrReadOnly,
    ]
    pagination_class = None


class FavoriteView(APIView):
    permission_classes = [
        IsAuthorOrStaffOrReadOnly,
    ]

    def post(self, request, recipe_id):
        user = get_object_or_404(User, username=request.user.username)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        data = {"user": user.id, "recipe": recipe.id}
        serializer = AddToFavoriteSerializer(
            data=data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = get_object_or_404(User, username=request.user.username)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        favorite = FavoriteRecipes.objects.filter(user=user, recipe=recipe)
        if favorite.exists():
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Рецепт в списке избранных не найден"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ShoppingCartView(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, recipe_id):
        user = get_object_or_404(User, username=request.user.username)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(
                {"error": "Рецепт уже в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ShoppingCart.objects.create(user=user, recipe=recipe)
        serializer = MiniRecipe(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = get_object_or_404(User, username=request.user.username)
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Рецепт в списке покупок не найден"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class GetShoppingList(APIView):
    def get(self, request):
        shopping_cart = make_shopping_cart(request)
        response = HttpResponse(shopping_cart, "Content-Type: text/plain")
        response["Content-Disposition"] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
