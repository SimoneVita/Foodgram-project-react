from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag, TagsRecipes)
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .pagination import CustomPaginator
from .permissions import CustomPermission, IsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscribeCartSerializer, TagSerializer)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    lookup_field = 'id'
    http_method_names = ['get']
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'id'
    http_method_names = ['get']
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (CustomPermission, )
    http_method_names = ['get', 'post', 'patch', 'delete']
    lookup_field = 'id'
    pagination_class = CustomPaginator

    def get_queryset(self):
        queryset = self.queryset
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags
            ).distinct()
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)
        user = self.request.user
        if user.is_anonymous:
            return queryset
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart'
        )
        if is_in_shopping_cart in ('1', 'true'):
            queryset = queryset.filter(shopping_cart__user=user.id)
        elif is_in_shopping_cart in ('0', 'false'):
            queryset = queryset.exclude(shopping_cart__user=user.id)
        is_favorited = self.request.query_params.get('is_favorited')
        if is_favorited in ('1', 'true'):
            queryset = queryset.filter(favorite__user=user.id)
        if is_favorited in ('0', 'false'):
            queryset = queryset.exclude(favorite__user=user.id)
        return queryset

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)

    def add_model(self, model, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        serializer = SubscribeCartSerializer(
            recipe,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        model.objects.create(user=user, recipe=recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def remove_model(self, model, user, id):
        recipe = get_object_or_404(Recipe, id=id)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже был удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, id):
        if request.method == 'POST':
            return self.add_model(Favorite, request, id)
        return self.remove_model(Favorite, request.user, id)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, id):
        if request.method == 'POST':
            return self.add_model(ShoppingCart, request, id)
        return self.remove_model(ShoppingCart, request.user, id)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        filename = f'{user}_cart.txt'
        final_list = []
        for i in ingredients:
            final_list.append(f'{i["ingredient__name"]}'
                              f' - {i["amount"]}'
                              f' {i["ingredient__measurement_unit"]}'
                              )
        file = HttpResponse('Cписок покупок:\n' + '\n'.join(final_list),
                            content_type='application.txt')
        file['Content-Disposition'] = (
            f'attachment; filename={filename}')
        return file
