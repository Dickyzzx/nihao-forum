from django.contrib import admin
from schools.models import School
from .models import InviteCode

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'inviter', 'used_by', 'used', 'created_at')
    list_filter = ('used',)
    search_fields = ('code', 'inviter__username', 'used_by__username')