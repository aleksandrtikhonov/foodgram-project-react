from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from recipes.models import Recipe
from recipes.serializers import MiniRecipe
from rest_framework import serializers

from .models import Follow

User = get_user_model()

class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'password',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(author=obj, user=user).exists()


class ManageSubscribeSerizlizer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        record = Recipe.objects.filter(author=obj)
        return MiniRecipe(record, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class CurrentUserSubscriptionsSerizlizer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        recipes_limit = int(self.context.get('request').GET["recipes_limit"])
        record = Recipe.objects.filter(author=obj)[:recipes_limit]
        return MiniRecipe(record, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()