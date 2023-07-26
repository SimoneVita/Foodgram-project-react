from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = DefaultRouter()
router.register(
    r'ingredients',
    IngredientViewSet,
)
router.register(
    r'tags', TagViewSet
)
router.register(
    r'recipes',
    RecipeViewSet,
)

urlpatterns = [
    path('', include('users.urls')),
    path('', include(router.urls)),
]
