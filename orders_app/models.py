from django.conf import settings
from django.db import models

from offers_app.models import OfferDetail


class Order(models.Model):
    """An order with a snapshot of the ordered offer detail.

    Title, price and the other detail fields are copied on creation,
    so later changes to the offer do not affect existing orders.
    """

    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders',
    )
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_orders',
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(
        max_length=10, choices=OfferDetail.OFFER_TYPE_CHOICES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return id, title and status of the order."""
        return f'Order {self.id}: {self.title} ({self.status})'
