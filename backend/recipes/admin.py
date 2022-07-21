from django.contrib import admin
from django.forms.models import BaseInlineFormSet

from .models import (FavoriteRecipes, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)


class RequiredInlineFormSet(BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super(RequiredInlineFormSet, self)._construct_form(i, **kwargs)
        form.empty_permitted = False
        return form


class RecipeIngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through
    formset = RequiredInlineFormSet
    extra = 3


class RecipeTagInline(admin.TabularInline):
    model = Recipe.tags.through
    formset = RequiredInlineFormSet


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "name",
        "author",
        "get_ingredients",
        "cooking_time",
        "get_tags",
        "get_favorites",
    )
    search_fields = (
        "name",
        "author__first_name",
        "author__last_name",
        "author__username",
        "tags__name",
    )
    list_filter = ("author", "name", "tags")
    empty_value_display = "-пусто-"
    inlines = (RecipeTagInline, RecipeIngredientInline)

    @admin.display(description="ингредиенты")
    def get_ingredients(self, obj):
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )

    @admin.display(description="теги")
    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    @admin.display(description="добавлено в избранное")
    def get_favorites(self, obj):
        return obj.favorites_recipe.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    search_fields = ("name",)
    empty_value_display = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "color", "slug")
    list_editable = ("name", "color", "slug")


class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "tag")
    list_editable = ("recipe", "tag")


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredient", "amount")
    list_editable = ("recipe", "ingredient", "amount")


class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "user")
    list_editable = ("recipe", "user")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "user")
    list_editable = ("recipe", "user")


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(FavoriteRecipes, FavoriteRecipesAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
