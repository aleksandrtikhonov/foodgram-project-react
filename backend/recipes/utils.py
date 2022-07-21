from django.db.models import Sum

from .models import RecipeIngredient


def make_shopping_cart(request):
    ingredients = (
        RecipeIngredient.objects.filter(
            recipe__carts_recipe__user=request.user)
        .values_list("ingredient__name", "ingredient__measurement_unit")
        .annotate(amount=Sum("amount"))
    )
    shopping_cart = "\n".join(
        [
            f"{ingredient_name} ({measurement_unit}) - {amount}"
            for ingredient_name, measurement_unit, amount in ingredients
        ]
    )
    return shopping_cart
