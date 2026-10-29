from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profil', {'fields': ('type', 'file', 'location', 'tel', 'description', 'working_hours')}),
    )
    list_display = ('username', 'email', 'type', 'is_staff')
