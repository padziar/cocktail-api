from django.core.validators import MinValueValidator
from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_alcoholic = models.BooleanField(default=False)
    image_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Cocktail(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.CharField(max_length=100)
    instructions = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through="CocktailIngredient",
        related_name="cocktails",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CocktailIngredient(models.Model):
    class Unit(models.TextChoices):
        ML = "ml", "ml"
        CL = "cl", "cl"
        G = "g", "g"
        PIECE = "pcs", "pieces"
        TSP = "tsp", "teaspoon"
        TBSP = "tbsp", "tablespoon"
        DASH = "dash", "dash"
        LEAVES = "leaves", "leaves"

    cocktail = models.ForeignKey(
        Cocktail,
        on_delete=models.CASCADE,
        related_name="cocktail_ingredients",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name="cocktail_ingredients",
    )
    amount = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.ML)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cocktail", "ingredient"],
                name="unique_ingredient_per_cocktail",
            )
        ]

    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient} in {self.cocktail}"