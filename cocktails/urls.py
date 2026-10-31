from rest_framework.routers import DefaultRouter

from .views import CocktailViewSet, IngredientViewSet

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredient")
router.register("cocktails", CocktailViewSet, basename="cocktail")

urlpatterns = router.urls