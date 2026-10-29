from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    business_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='written_reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business_user', 'reviewer'],
                name='unique_review_per_business',
            )
        ]

    def __str__(self):
        return f'{self.reviewer.username} → {self.business_user.username}: {self.rating}'
