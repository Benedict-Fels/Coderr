from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

PROFILE_FIELDS = (
    'type', 'file', 'location', 'tel', 'description', 'working_hours',
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Django's user admin extended by the profile fields."""

    fieldsets = UserAdmin.fieldsets + (
        ('Profil', {'fields': PROFILE_FIELDS}),
    )
    list_display = ('username', 'email', 'type', 'is_staff')
