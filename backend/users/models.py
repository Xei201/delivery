from django.contrib.auth.models import AbstractUser
from django.db import models
from _decimal import Decimal


class CustomUser(AbstractUser):
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, verbose_name="Баланс"
    )

    def write_off_balance(self, total_price: Decimal) -> None:
        """
        Проверяет возможность списания суммы с баланса пользователя и списывает её
        :param total_price: сумма списания с баланса
        :return: None
        """
        if self.balance < total_price:
            raise Exception("Сумма списания превышает средства на балансе")
        self.balance -= total_price
        self.save()
