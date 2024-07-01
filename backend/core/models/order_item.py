from django.db import models
from django.utils.translation import gettext as _

from .dish import Dish
from .order import Order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = _("Позиция")
        verbose_name_plural = _("Позиции")

    def __str__(self):
        return f"{self.quantity} {self.dish}"

