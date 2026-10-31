from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cocktail, CocktailIngredient, Ingredient


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.rum = Ingredient.objects.create(name="Rum", is_alcoholic=True)
        self.mint = Ingredient.objects.create(name="Mint")
        self.lime = Ingredient.objects.create(name="Lime juice")
        self.soda = Ingredient.objects.create(name="Soda water")

    def make_cocktail(self, name, ingredients, category="Long drink"):
        cocktail = Cocktail.objects.create(
            name=name, category=category, instructions="Mix."
        )
        for ingredient in ingredients:
            CocktailIngredient.objects.create(
                cocktail=cocktail, ingredient=ingredient, amount=10, unit="ml"
            )
        return cocktail


class IngredientAPITests(BaseAPITestCase):
    def test_list_is_paginated(self):
        response = self.client.get("/api/ingredients/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 4)
        self.assertIn("results", response.data)

    def test_create_ingredient(self):
        payload = {"name": "Gin", "description": "Spirit", "is_alcoholic": True}
        response = self.client.post("/api/ingredients/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ingredient.objects.filter(name="Gin").exists())

    def test_create_rejects_too_short_name(self):
        response = self.client.post("/api/ingredients/", {"name": "a"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_rejects_duplicate_name(self):
        response = self.client.post("/api/ingredients/", {"name": "Rum"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ingredient(self):
        response = self.client.patch(
            f"/api/ingredients/{self.mint.id}/",
            {"description": "Fresh"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mint.refresh_from_db()
        self.assertEqual(self.mint.description, "Fresh")

    def test_delete_unused_ingredient(self):
        response = self.client.delete(f"/api/ingredients/{self.soda.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_used_ingredient_returns_conflict(self):
        self.make_cocktail("Mojito", [self.rum, self.mint])
        response = self.client.delete(f"/api/ingredients/{self.rum.id}/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertTrue(Ingredient.objects.filter(id=self.rum.id).exists())

    def test_filter_by_is_alcoholic(self):
        response = self.client.get("/api/ingredients/?is_alcoholic=true")
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Rum")


class CocktailAPITests(BaseAPITestCase):
    def valid_payload(self):
        return {
            "name": "Mojito",
            "category": "Long drink",
            "instructions": "Muddle mint, add rum, top with soda.",
            "ingredients": [
                {"ingredient": self.rum.id, "amount": "50.00", "unit": "ml"},
                {"ingredient": self.mint.id, "amount": "10.00", "unit": "leaves"},
            ],
        }

    def test_create_cocktail_with_ingredients(self):
        response = self.client.post("/api/cocktails/", self.valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["ingredients"]), 2)
        self.assertEqual(CocktailIngredient.objects.count(), 2)

    def test_create_rejects_empty_ingredients(self):
        payload = self.valid_payload()
        payload["ingredients"] = []
        response = self.client.post("/api/cocktails/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Cocktail.objects.count(), 0)

    def test_create_rejects_repeated_ingredient(self):
        payload = self.valid_payload()
        payload["ingredients"][1]["ingredient"] = self.rum.id
        response = self.client.post("/api/cocktails/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_unknown_ingredient(self):
        payload = self.valid_payload()
        payload["ingredients"][0]["ingredient"] = 9999
        response = self.client.post("/api/cocktails/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rejects_non_positive_amount(self):
        payload = self.valid_payload()
        payload["ingredients"][0]["amount"] = "0"
        response = self.client.post("/api/cocktails/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_cocktail(self):
        cocktail = self.make_cocktail("Mojito", [self.rum, self.mint])
        response = self.client.get(f"/api/cocktails/{cocktail.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Mojito")
        self.assertEqual(len(response.data["ingredients"]), 2)

    def test_patch_without_ingredients_keeps_them(self):
        cocktail = self.make_cocktail("Mojito", [self.rum, self.mint])
        response = self.client.patch(
            f"/api/cocktails/{cocktail.id}/", {"category": "Shot"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cocktail.refresh_from_db()
        self.assertEqual(cocktail.category, "Shot")
        self.assertEqual(cocktail.cocktail_ingredients.count(), 2)

    def test_patch_with_ingredients_replaces_them(self):
        cocktail = self.make_cocktail("Mojito", [self.rum, self.mint])
        payload = {"ingredients": [{"ingredient": self.lime.id, "amount": "20", "unit": "ml"}]}
        response = self.client.patch(
            f"/api/cocktails/{cocktail.id}/", payload, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = list(cocktail.cocktail_ingredients.values_list("ingredient_id", flat=True))
        self.assertEqual(ids, [self.lime.id])

    def test_delete_cocktail_keeps_ingredients(self):
        cocktail = self.make_cocktail("Mojito", [self.rum, self.mint])
        response = self.client.delete(f"/api/cocktails/{cocktail.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CocktailIngredient.objects.count(), 0)
        self.assertEqual(Ingredient.objects.count(), 4)

    def test_list_is_paginated(self):
        self.make_cocktail("Mojito", [self.rum, self.mint])
        response = self.client.get("/api/cocktails/")
        self.assertEqual(response.data["count"], 1)
        self.assertIn("results", response.data)


class CocktailFilterTests(BaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.make_cocktail("Mojito", [self.rum, self.mint, self.soda])
        self.make_cocktail(
            "Virgin Mojito", [self.mint, self.lime, self.soda], category="Mocktail"
        )

    def names(self, query):
        response = self.client.get(f"/api/cocktails/?{query}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return [item["name"] for item in response.data["results"]]

    def test_non_alcoholic_with_mint(self):
        self.assertEqual(
            self.names("is_alcoholic=false&ingredient=mint"), ["Virgin Mojito"]
        )

    def test_alcoholic_only(self):
        self.assertEqual(self.names("is_alcoholic=true"), ["Mojito"])

    def test_multiple_ingredients_must_all_match(self):
        self.assertEqual(self.names("ingredient=mint,lime"), ["Virgin Mojito"])

    def test_filter_by_category_case_insensitive(self):
        self.assertEqual(self.names("category=mocktail"), ["Virgin Mojito"])

    def test_filter_by_name(self):
        self.assertEqual(self.names("name=virgin"), ["Virgin Mojito"])

    def test_search_by_ingredient_name(self):
        self.assertEqual(self.names("search=rum"), ["Mojito"])

    def test_ordering_descending(self):
        self.assertEqual(self.names("ordering=-name"), ["Virgin Mojito", "Mojito"])

    def test_invalid_filter_value_returns_400(self):
        response = self.client.get("/api/cocktails/?ingredient_id=xyz")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)