from decimal import Decimal
from django.test import TestCase
from users.models import CustomUser


class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', password='password123', balance=Decimal('100.00')
        )

    def test_write_off_balance_success(self):
        self.user.write_off_balance(Decimal('50.00'))
        self.assertEqual(self.user.balance, Decimal('50.00'))

    def test_write_off_balance_insufficient_funds(self):
        with self.assertRaises(Exception) as context:
            self.user.write_off_balance(Decimal('150.00'))
        self.assertEqual(str(context.exception), 'Сумма списания превышает средства на балансе')
