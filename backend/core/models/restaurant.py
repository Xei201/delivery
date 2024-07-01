from django.db import models
from django.utils.translation import gettext as _


class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название заведения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = _("Ресторан")
        verbose_name_plural = _("Рестораны")

    def __str__(self):
        return self.name
