import django_filters
from django.db.models import Exists, OuterRef

from .models import Cocktail, CocktailIngredient, Ingredient


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ["name", "is_alcoholic"]


class CocktailFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(lookup_expr="iexact")
    is_alcoholic = django_filters.BooleanFilter(method="filter_is_alcoholic")
    ingredient = django_filters.CharFilter(
        method="filter_ingredient",
        help_text="Comma-separated ingredient names (cocktail must contain all).",
    )
    ingredient_id = django_filters.NumberFilter(method="filter_ingredient_id")

    class Meta:
        model = Cocktail
        fields = ["name", "category"]

    def filter_is_alcoholic(self, queryset, name, value):
        has_alcohol = CocktailIngredient.objects.filter(
            cocktail=OuterRef("pk"), ingredient__is_alcoholic=True
        )
        if value:
            return queryset.filter(Exists(has_alcohol))
        return queryset.exclude(Exists(has_alcohol))

    def filter_ingredient(self, queryset, name, value):
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            match = CocktailIngredient.objects.filter(
                cocktail=OuterRef("pk"), ingredient__name__icontains=part
            )
            queryset = queryset.filter(Exists(match))
        return queryset

    def filter_ingredient_id(self, queryset, name, value):
        match = CocktailIngredient.objects.filter(
            cocktail=OuterRef("pk"), ingredient_id=value
        )
        return queryset.filter(Exists(match))