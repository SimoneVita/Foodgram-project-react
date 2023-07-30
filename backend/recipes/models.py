from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from users.models import User

MIN_VALUE = 1
MAX_VALUE = 32000


class Ingredient(models.Model):
    """Ингредиенты."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=100
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Тег."""
    name = models.CharField(
        verbose_name='Название',
        unique=True,
        max_length=200
    )
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=(
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Пример цвета в формате HEX: #a2ff01'
            ),
        )
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=200
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Рецепт."""
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
        null=True,
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message='Время приготовления не может быть меньше минуты'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='32000 минут? Серьезно?'
            ),
        )
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagsRecipes',
        related_name='recipes',
        verbose_name='Теги',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagsRecipes(models.Model):
    tags = models.ForeignKey(
        Tag,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Теги'
    )
    recipes = models.ForeignKey(
        Recipe,
        null=False,
        on_delete=models.CASCADE,
        verbose_name='Рецепты'
    )

    class Meta:
        ordering = ['-recipes']
        verbose_name = 'Тег в рецепте'
        verbose_name_plural = 'Теги и рецептах'
        constraints = [
            models.UniqueConstraint(fields=['tags', 'recipes'],
                                    name='unique_TagsinRecipes')
        ]


class IngredientRecipe(models.Model):
    """Отношение произведения к жанру."""
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredientrecipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredientrecipe'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                MIN_VALUE,
                message='Время приготовления не может быть меньше минуты'
            ),
            MaxValueValidator(
                MAX_VALUE,
                message='32000 минут? Серьезно?'
            ),
        )
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент в рецепт'
        verbose_name_plural = 'Ингредиенты в рецептах'

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.ingredient.measurement_unit})'
            f' - {self.amount} '
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='favorite',
        verbose_name='Пользователь',
        help_text='Тот, кто подписался',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        related_name='favorite',
        verbose_name='Рецепт',
        help_text='Рецепт, на который подписались',
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe_favourite')
        ]

    def __str__(self):
        return f'{self.recipe} добавлен(а) {self.user} в Избранное'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        null=False,
        related_name='shopping_cart',
        verbose_name='Рецепт',
        help_text='Рецепт, добавленный в список покупок',
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe_cart')
        ]

    def __str__(self):
        return f'{self.recipe} добавлен(а) {self.user} в Список покупок'
