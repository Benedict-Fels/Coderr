from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    TYPE_CHOICES = [('customer', 'Customer'), ('business', 'Business')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    file = models.ImageField(upload_to='profile_pictures/', blank=True)
    location = models.CharField(max_length=100, blank=True, default='')
    tel = models.CharField(max_length=30, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=50, blank=True, default='')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} ({self.type})'
