from django.db import transaction
from rest_framework import serializers

from .models import Cocktail, CocktailIngredient, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name", "description", "is_alcoholic", "image_url"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must have at least 2 characters.")
        return value


class CocktailIngredientSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)

    class Meta:
        model = CocktailIngredient
        fields = ["ingredient", "ingredient_name", "amount", "unit"]


class CocktailSerializer(serializers.ModelSerializer):
    ingredients = CocktailIngredientSerializer(
        source="cocktail_ingredients", many=True
    )

    class Meta:
        model = Cocktail
        fields = [
            "id",
            "name",
            "category",
            "instructions",
            "ingredients",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name must have at least 2 characters.")
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("A cocktail needs at least one ingredient.")
        ids = [item["ingredient"].id for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Ingredients must not repeat.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("cocktail_ingredients")
        cocktail = Cocktail.objects.create(**validated_data)
        CocktailIngredient.objects.bulk_create(
            CocktailIngredient(cocktail=cocktail, **item) for item in items
        )
        return cocktail

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop("cocktail_ingredients", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items is not None:
            instance.cocktail_ingredients.all().delete()
            CocktailIngredient.objects.bulk_create(
                CocktailIngredient(cocktail=instance, **item) for item in items
            )
        return instance