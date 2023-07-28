from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        ReadOnlyField)
from users.serializers import CustomUserSerializer

MIN_VALUE = 1
MAX_VALUE = 32000


class IngredientSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Ingredient


class TagSerializer(ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class IngredientRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')
    amount = IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientRecipe


class RecipeSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(
        source='ingredientrecipe',
        many=True,
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE
    )

    class Meta:
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time')
        model = Recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        user = request.user
        return (request.user.is_authenticated
                and user.favorite.filter(recipe=obj).exists()
                )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        user = request.user
        return (request.user.is_authenticated
                and user.shopping_cart.filter(recipe=obj).exists()
                )

    def validate(self, data):
        user = self.context.get('request').user
        request_method = self.context.get('request').method
        recipe_name = data['name']
        if user and recipe_name and request_method == 'POST':
            if user.recipes.filter(name=recipe_name).exists():
                raise serializers.ValidationError(
                    'Такой рецепт уже существует!')
        t_list = self.initial_data['tags']
        if not t_list:
            raise serializers.ValidationError(
                'Нужно добавить минимум 1 тег!'
            )
        unique_tags = list(set(t_list))
        if len(t_list) > len(unique_tags):
            raise serializers.ValidationError(
                'Запрещается добавлять одинаковые теги!'
            )
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Блюдо должно содержать хотя бы 1 ингредиент!')
        i_set = set()
        for i in ingredients:
            ingredient = get_object_or_404(Ingredient,
                                           id=i['id'])
            if ingredient in i_set:
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient.name} уже добавлен!')
            i_set.add(ingredient)
        data['ingredients'] = ingredients
        return data

    def ingredientsrecipe_create(self, ingredients, recipe):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        tags = self.initial_data.get('tags')
        recipe.tags.set(tags)
        self.ingredientsrecipe_create(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        tags = self.initial_data.get('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.ingredientsrecipe_create(ingredients, instance)
        instance.save()
        return instance


class SubscribeCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)

    def validate(self, data):
        user = self.context.get('request').user
        recipe = self.instance
        if (
                'favorite' in self.context['request'].path
        ) and (
                Favorite.objects.filter(
                    user=user,
                    recipe=recipe
                ).exists()
        ):
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже был добавлен!'}
            )
        elif (
                'shopping_cart' in self.context['request'].path
        ) and (
                ShoppingCart.objects.filter(
                    user=user,
                    recipe=recipe
                ).exists()
        ):
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже был добавлен!'}
            )
        return data
