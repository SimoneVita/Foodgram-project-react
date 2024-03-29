from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import User
from .validators import (validate_email, validate_username,
                         validate_username_exists)


class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[validate_username, validate_username_exists],
        allow_blank=False
    )
    email = serializers.EmailField(max_length=254,
                                   validators=[validate_email],
                                   allow_blank=False)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return user.follower.filter(author=obj).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        )


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user == author:
            raise serializers.ValidationError(
                'На самого себя может подписаться только Бузова!')
        if author.following.filter(user=user).exists():
            raise serializers.ValidationError(
                'Уже есть подписка на данного пользователя!')
        return data

    def get_recipes(self, obj):
        from api.serializers import SubscribeCartSerializer
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = obj.recipes.all()
        if limit:
            queryset = queryset[:int(limit)]
        return SubscribeCartSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
