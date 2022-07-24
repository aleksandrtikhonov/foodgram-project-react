from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import exceptions, serializers

from recipes.models import (FavoriteRecipes, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from users.models import Follow

User = get_user_model()


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "password",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False
        user = request.user
        return Follow.objects.filter(author=obj, user=user).exists()


class ManageSubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField("get_recipes")
    recipes_count = serializers.ReadOnlyField(source="recipe_author.count")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        record = Recipe.objects.filter(author=obj)
        return MiniRecipe(record, many=True).data


class CurrentUserSubscriptionsSeriazlizer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.ReadOnlyField(source="recipe_author.count")

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit:
            record = Recipe.objects.filter(author=obj)[: int(recipes_limit)]
        else:
            record = Recipe.objects.all()
        return MiniRecipe(record, many=True).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ("amount", "id")


class RecipeReadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True, many=False)
    ingredients = serializers.SerializerMethodField("get_ingredients")
    tags = serializers.SerializerMethodField("get_tags")
    image = serializers.ReadOnlyField(source="image.url")
    is_favorited = serializers.SerializerMethodField("get_is_favorited")
    is_in_shopping_cart = serializers.SerializerMethodField(
        "get_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "image",
            "tags",
            "cooking_time",
            "text",
            "name",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_ingredients(self, obj):
        record = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientsForRecipe(record, many=True).data

    def get_tags(self, obj):
        record = RecipeTag.objects.filter(recipe=obj)
        return TagsForRecipe(record, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = request.user
        if user.is_anonymous:
            return False
        return FavoriteRecipes.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        user = request.user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField(use_url=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = "__all__"

    def bulk_create_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient["id"],
                    amount=ingredient["amount"],
                )
                for ingredient in ingredients_data
            ]
        )
    def chek_ingredients(self, ingredients_data):
        ingredient_list = []
        for ingredient in ingredients_data:
            if ingredient["id"] in ingredient_list:
                raise serializers.ValidationError(
                    "Ингредиенты должны быть уникальными"
                )
            ingredient_list.append(ingredient["id"])
            if int(ingredient["amount"]) <= 0:
                raise exceptions.ValidationError(
                    f"Количество ингредиента {ingredient['id']} "
                    "не должно быть меньше единицы"
                )
        return ingredients_data

    def validate(self, data):
        ingredients_data = data.get('ingredients')
        tags_data = data.get('tags')
        if len(tags_data) != len(set(tags_data)):
            raise serializers.ValidationError(
                "Теги должны быть уникальными"
            )

        if not data.get('name'):
            raise serializers.ValidationError(
                "Название рецепта не может быть пустым"
            )
        if not data.get('tags'):
            raise serializers.ValidationError(
                "У рецепта должен быть хотя бы один тег"
            )
        if not data.get('text'):
            raise serializers.ValidationError(
                "Описание рецепта не может быть пустым"
            )
        cooking_time = data.get('cooking_time')
        if not cooking_time:
            raise serializers.ValidationError(
                "У рецета должно быть указано время готовки"
            )
        if int(cooking_time) < 0:
            raise serializers.ValidationError(
                "Время готовки должно быть положительным числом"
            )
        self.chek_ingredients(ingredients_data)

        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        request = self.context.get("request")
        recipe = Recipe.objects.create(author=request.user, **validated_data)
        recipe.save()
        recipe.tags.set(tags_data)
        self.bulk_create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance: Recipe, validated_data):
        instance.cooking_time = validated_data.get("cooking_time")
        instance.name = validated_data.get("name")
        instance.text = validated_data.get("text")
        instance.tags.set(validated_data.get("tags"))
        if validated_data.get("image"):
            instance.image = validated_data.get("image")
        ingredients_data = validated_data.pop("ingredients")
        instance.ingredients.clear()
        self.bulk_create_ingredients(instance, ingredients_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data


class IngredientsForRecipe(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class TagsForRecipe(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="tag.id")
    name = serializers.ReadOnlyField(source="tag.name")
    color = serializers.ReadOnlyField(source="tag.color")
    slug = serializers.ReadOnlyField(source="tag.slug")

    class Meta:
        model = RecipeTag
        fields = ("id", "name", "color", "slug")


class MiniRecipe(RecipeReadSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class AddToFavoriteSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = data["user"]
        recipe = data["recipe"]
        if FavoriteRecipes.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                {"error": "Рецепт уже в избранном"})
        return data

    def to_representation(self, instance: FavoriteRecipes):
        return MiniRecipe(instance.recipe).data

    class Meta:
        fields = ("user", "recipe")
        model = FavoriteRecipes
