from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """기본 UserAdmin에 nickname/bio 필드를 노출한 커스텀 Admin."""

    list_display = ['username', 'nickname', 'email', 'is_staff', 'date_joined']
    search_fields = ['username', 'nickname', 'email']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'bio')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {'fields': ('nickname', 'bio')}),
    )
