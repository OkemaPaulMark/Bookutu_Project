from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'is_active', 'is_verified', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_active', 'is_verified')
