from django.contrib import admin

from .models import Subscriptions, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'is_superuser',
                    )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'author',
                    )
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscriptions, SubscriptionsAdmin)
