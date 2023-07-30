from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag, TagsRecipes)


class IngredientRecipeInline(admin.StackedInline):
    model = IngredientRecipe
    min_num = 1


class TagRecipeInline(admin.TabularInline):
    model = TagsRecipes
    min_num = 1


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit',
                    )


class TagsRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipes',
                    'tags',
                    )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'color',
                    'slug',
                    )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'author',
                    )
    list_filter = ('name', 'author',
                   ('tags', admin.RelatedOnlyFieldListFilter),)
    inlines = (IngredientRecipeInline, TagRecipeInline)


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe',
                    'ingredient',
                    'amount',
                    )
    list_filter = ('ingredient',)


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe',
                    'user',
                    )


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe',
                    'user',
                    )


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(TagsRecipes, TagsRecipesAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
