from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with the profile fields required by the API.

    Inherits username, email, first_name, last_name, password and
    date_joined from AbstractUser. The type may be empty for admins,
    but is required on registration.
    """

    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, blank=True, default='')
    file = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    tel = models.CharField(max_length=30, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        """Return the username together with the user type."""
        return f'{self.username} ({self.type})'
