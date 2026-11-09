from django.conf import settings
from django.db import models


class Offer(models.Model):
    """An offer created by a business user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
    )
    title = models.CharField(max_length=255)
    image = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return the offer title."""
        return self.title


class OfferDetail(models.Model):
    """One of the three packages (basic, standard, premium) of an offer."""

    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    offer = models.ForeignKey(
        Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        """Return the offer title together with the package type."""
        return f'{self.offer.title} – {self.offer_type}'
