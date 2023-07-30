from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

from product.models import Car

methods_options = [
    ('upi', 'UPI'),
    ('cash', 'Cash'),
    ('netbanking', 'NetBanking')
]

status_options = [
    ('pending', 'Pending'),
    ('complete', 'Complete'),
    ('failed', 'Failed')
]

class Order(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, blank=True, null=True, related_name="order")
    customer = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    payment_method = models.CharField(max_length=250, blank=False, null=False, choices=methods_options)
    payment_status = models.CharField(max_length=250, blank=False, null=False, choices=status_options)
    order_date = models.DateTimeField(default=timezone.now(), blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.customer}_{self.car}'