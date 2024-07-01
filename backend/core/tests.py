from django.test import TestCase
from core.models import Dish, Order, OrderItem, Restaurant
from users.models import CustomUser
from decimal import Decimal


class CoreModelsTestCase(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(name='Test Restaurant')
        self.dish = Dish.objects.create(name='Test Dish', price=Decimal('10.00'), restaurant=self.restaurant)
        self.user = CustomUser.objects.create_user(username='testuser', password='password')
        self.order = Order.objects.create(user=self.user)

    def test_create_dish(self):
        self.assertEqual(self.dish.name, 'Test Dish')
        self.assertEqual(self.dish.price, Decimal('10.00'))

    def test_create_order(self):
        self.assertEqual(self.order.user, self.user)

    def test_create_order_item(self):
        order_item = OrderItem.objects.create(order=self.order, dish=self.dish, quantity=2)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.dish, self.dish)
