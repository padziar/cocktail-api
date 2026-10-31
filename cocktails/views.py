from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Cocktail, Ingredient
from .serializers import CocktailSerializer, IngredientSerializer
from .filters import CocktailFilter, IngredientFilter
from drf_spectacular.utils import extend_schema


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "id"]
    
    @extend_schema(
        responses={
            204: None,
            409: {
                "type": "object",
                "properties": {"detail": {"type": "string"}},
            },
        }
    )
    

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Ingredient is used in a cocktail and cannot be deleted."},
                status=status.HTTP_409_CONFLICT,
            )


class CocktailViewSet(viewsets.ModelViewSet):
    queryset = Cocktail.objects.prefetch_related(
        "cocktail_ingredients__ingredient"
    )
    serializer_class = CocktailSerializer
    filterset_class = CocktailFilter
    search_fields = ["name", "category", "ingredients__name"]
    ordering_fields = ["name", "category", "created_at"]