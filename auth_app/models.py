from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Eigenes User-Model: Djangos User + die Profilfelder aus der Doku.

    Von AbstractUser geerbt: username, email, first_name, last_name,
    password und date_joined (wird in der API als created_at ausgegeben).
    """

    TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('business', 'Business'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True, default='')
    file = models.CharField(max_length=255, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    tel = models.CharField(max_length=30, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=50, blank=True, default='')

    def __str__(self):
        return f'{self.username} ({self.type})'
