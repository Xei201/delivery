from django.db import models
from django.utils.translation import gettext as _

from .restaurant import Restaurant


class Dish(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    restaurant = models.ForeignKey(Restaurant, related_name='dishes', on_delete=models.CASCADE, verbose_name="Заведение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = _("Блюда")
        verbose_name_plural = _("Блюда")

    def __str__(self):
        return self.name
