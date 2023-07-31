from django.core.validators import MinValueValidator, MaxValueValidator
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import (ModelSerializer,
                                        ReadOnlyField)

from recipes.models import (Ingredient, IngredientRecipe, Recipe,
                            Tag)
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
    amount = serializers.ReadOnlyField(
        validators=[
            MinValueValidator(MIN_VALUE),
            MaxValueValidator(MAX_VALUE)
        ]
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

    def recipe_check(self, user, request_method, recipe):
        if user and recipe and request_method == 'POST':
            if user.recipes.filter(name=recipe).exists():
                raise serializers.ValidationError(
                    'Такой рецепт уже существует!')
        return user

    def tags_check(self, tag_list):
        if not tag_list:
            raise serializers.ValidationError(
                'Нужно добавить минимум 1 тег!'
            )
        unique_tags = list(set(tag_list))
        if len(tag_list) > len(unique_tags):
            raise serializers.ValidationError(
                'Запрещается добавлять одинаковые теги!'
            )
        return unique_tags

    def ingredients_check(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Блюдо должно содержать хотя бы 1 ингредиент!')
        ingredients_set = set()
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=item['id']
            )
            if ingredient in ingredients_set:
                raise serializers.ValidationError(
                    f'Ингредиент {ingredient.name} уже добавлен!')
            ingredients_set.add(ingredient)
            if int(item['amount']) < MIN_VALUE:
                raise serializers.ValidationError(
                    f'Количество ингредиента {ingredient.name} < {MIN_VALUE}'
                )
            if int(item['amount']) > MAX_VALUE:
                raise serializers.ValidationError(
                    f'Количество ингредиента {ingredient.name} > {MAX_VALUE}'
                )
        return ingredients

    def validate(self, data):
        user = self.context.get('request').user
        request_method = self.context.get('request').method
        recipe_name = data['name']
        tag_list = self.initial_data['tags']
        ingredients = self.initial_data.get('ingredients')
        data['author'] = self.recipe_check(user,
                                           request_method,
                                           recipe_name)
        data['tags'] = self.tags_check(tag_list)
        data['ingredients'] = self.ingredients_check(ingredients)
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
        tags = validated_data.pop('tags')
        author = validated_data.pop('author')
        new_recipe = Recipe.objects.create(
            author=author,
            **validated_data
        )
        new_recipe.tags.set(tags)
        self.ingredientsrecipe_create(ingredients, new_recipe)
        return new_recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        tags = validated_data.pop('tags')
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
                user.favorite.filter(
                    recipe=recipe
                ).exists()
        ):
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже был добавлен!'}
            )
        if (
                'shopping_cart' in self.context['request'].path
        ) and (
                user.shopping_cart.filter(
                    recipe=recipe
                ).exists()
        ):
            raise serializers.ValidationError(
                {'errors': 'Рецепт уже был добавлен!'}
            )
        return data
