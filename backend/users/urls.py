from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MyUserViewset

users_router = DefaultRouter()
users_router.register(r'users', MyUserViewset, basename='users')


urlpatterns = [
    path('', include(users_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
