from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_fields = ["is_alcoholic"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "id"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "Ingredient is used in a cocktail and cannot be deleted."},
                status=status.HTTP_409_CONFLICT,
            )