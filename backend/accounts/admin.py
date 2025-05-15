from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import InviteCode, CustomUser

@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'inviter', 'used_by', 'used', 'created_at')
    list_filter = ('used',)
    search_fields = ('code', 'inviter__username', 'used_by__username')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'nickname', 'email', 'school', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('nickname', 'school')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('nickname', 'school')}),
    )
