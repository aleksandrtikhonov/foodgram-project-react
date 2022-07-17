from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers
from users.models import Follow

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)

User = get_user_model()


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(author=obj, user=user).exists()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('amount', 'id')


class RecipeReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'image',
            'tags',
            'cooking_time',
            'text',
            'name',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart'
        )

    author = UserSerializer(read_only=True, many=False)
    ingredients = serializers.SerializerMethodField('get_ingredients')
    tags = serializers.SerializerMethodField('get_tags')
    image = serializers.SerializerMethodField('get_image')
    name = serializers.CharField()
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()
    is_favorited = serializers.SerializerMethodField('get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart')

    def get_ingredients(self, obj):
        record = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientsForRecipe(record, many=True).data

    def get_tags(self, obj):
        record = RecipeTag.objects.filter(recipe=obj)
        return TagsForRecipe(record, many=True).data

    def get_image(self, obj):
        return obj.image.url

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

    name = serializers.CharField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField(use_url=True)
    text = serializers.CharField()
    cooking_time = serializers.IntegerField()

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        request = self.context.get('request')
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        for ingredient in ingredients_data:
            if ingredient['amount'] <= 0:
                raise exceptions.ValidationError(
                    f"Количество ингредиента {ingredient['id']}"
                    "должно быть больше нуля"
                )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance: Recipe, validated_data):
        instance.cooking_time = validated_data.get('cooking_time')
        instance.name = validated_data.get('name')
        instance.text = validated_data.get('text')
        instance.tags.set(validated_data.get('tags'))
        if validated_data.get('image'):
            instance.image = validated_data.get('image')

        ingredients_data = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for ingredient in ingredients_data:
            if ingredient['amount'] <= 0:
                raise exceptions.ValidationError(
                    f"Количество ингредиента {ingredient['id']}"
                    "должно быть больше нуля"
                )
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class IngredientsForRecipe(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagsForRecipe(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='tag.id')
    name = serializers.ReadOnlyField(source='tag.name')
    color = serializers.ReadOnlyField(source='tag.color')
    slug = serializers.ReadOnlyField(source='tag.slug')

    class Meta:
        model = RecipeTag
        fields = ('id', 'name', 'color', 'slug')


class MiniRecipe(RecipeReadSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
