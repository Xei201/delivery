from _decimal import Decimal
from unittest.mock import patch

from rest_framework.test import APITestCase
from django.urls import reverse

from core.models import Restaurant, Dish, Order, OrderItem
from users.models import CustomUser


class AuthTests(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')

    def test_login_success(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Successfully logged in')

    def test_login_failure(self):
        url = reverse('login')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Invalid credentials')

    def test_logout(self):
        url = reverse('logout')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['detail'], 'Successfully logged out')


class RestaurantViewSetTest(APITestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        # Создаем рестораны
        self.restaurant1 = Restaurant.objects.create(name="Restaurant 1")
        self.restaurant2 = Restaurant.objects.create(name="Restaurant 2")

        # Создаем блюда для ресторанов
        self.dish1 = Dish.objects.create(name="Pizza", price=Decimal("10.00"), restaurant=self.restaurant1)
        self.dish2 = Dish.objects.create(name="Pasta", price=Decimal("12.00"), restaurant=self.restaurant1)
        self.dish3 = Dish.objects.create(name="Pizza Colcone", price=Decimal("12.00"), restaurant=self.restaurant1)
        self.dish4 = Dish.objects.create(name="Burger", price=Decimal("8.00"), restaurant=self.restaurant2)
        self.dish5 = Dish.objects.create(name="Salad", price=Decimal("6.00"), restaurant=self.restaurant2)

    def test_list_restaurants_not_authenticat(self):
        """
        Проверяет работу аутентификации
        :return:
        """
        url = reverse('restaurant-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)

    def test_list_restaurants(self):
        """
        Проверяет получение списка всех ресторанов.
        """
        url = reverse('restaurant-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'Restaurant 1')
        self.assertEqual(response.data[1]['name'], 'Restaurant 2')

    def test_filter_restaurants_by_dish_name(self):
        """
        Проверяет фильтрацию ресторанов по имени блюда.
        """
        url = f"{reverse('restaurant-list')}?dish_name=Pizza"

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(len(response.data[0]['dishes']), 2)
        self.assertEqual(response.data[0]['name'], 'Restaurant 1')

    def test_filter_restaurants_by_restaurant_id(self):
        """
        Проверяет фильтрацию ресторанов по ID ресторана.
        """
        url = f"{reverse('restaurant-list')}?restaurant_id={self.restaurant2.id}"

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Restaurant 2')

    def test_filter_restaurants_by_dish_name_and_restaurant_id(self):
        """
        Проверяет фильтрацию ресторанов по имени блюда и ID ресторана одновременно.
        """
        url = f"{reverse('restaurant-list')}?dish_name=Salad&restaurant_id={self.restaurant2.id}"

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Restaurant 2')

    def test_filter_restaurants_no_results(self):
        """
        Проверяет фильтрацию ресторанов по имени блюда, которое не существует. Ожидает возврата ошибки с кодом 403
        и соответствующим сообщением.
        """
        url = f"{reverse('restaurant-list')}?dish_name=Sushi"

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Ресторан не найден или у вас нет разрешения на его просмотр.')

    def test_filter_restaurants_invalid_restaurant_id(self):
        """
        Проверяет фильтрацию ресторанов по несуществующему ID ресторана. Ожидает возврата ошибки с кодом 403
        и соответствующим сообщением.
        """
        url = f"{reverse('restaurant-list')}?restaurant_id=999"

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Ресторан не найден или у вас нет разрешения на его просмотр.')

    def test_filter_restaurants_invalid_value_restaurant_id(self):
        """
        Проверяет фильтрацию ресторанов по некоректному ID ресторана. Ожидает возврата ошибки с кодом 403
        и соответствующим сообщением.
        """
        url = f"{reverse('restaurant-list')}?restaurant_id=abc"

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'], 'Указан не корректный ID ресторана')


class CartViewSetTest(APITestCase):

    def setUp(self):
        """
        Установка начальных данных для тестов.
        """
        self.user = CustomUser.objects.create_user(username='testuser', password='password123')
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.dish = Dish.objects.create(name="Test Dish", price=Decimal("10.00"), restaurant=self.restaurant)

    @patch('api.views.rd')
    def test_add_dish_to_cart_not_authenticat(self, mock_redis):
        """
        Проверяет работу аутентификации
        :return:
        """
        mock_redis.hincrby.return_value = None
        url = reverse('cart-add')
        data = {'dish_id': self.dish.id, 'quantity': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)

    @patch('api.views.rd')
    def test_add_dish_to_cart(self, mock_redis):
        """
        Проверка добавления блюда в корзину пользователя.
        """
        mock_redis.hincrby.return_value = None
        url = reverse('cart-add')
        data = {'dish_id': self.dish.id, 'quantity': 1}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        mock_redis.hincrby.assert_called_with(f'cart:{self.user.id}', self.dish.id, 1)

    @patch('api.views.rd')
    def test_delete_dish_from_cart(self, mock_redis):
        """
        Проверка удаления блюда из корзины пользователя.
        """
        mock_redis.hget.return_value = b'2'
        mock_redis.hdel.return_value = None
        mock_redis.hincrby.return_value = None

        url = reverse('cart-delete')
        data = {'dish_id': self.dish.id, 'quantity': 1}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        mock_redis.hincrby.assert_called_with(f'cart:{self.user.id}', self.dish.id, -1)

    @patch('api.views.rd')
    def test_list_cart(self, mock_redis):
        """
        Проверка получения всех товаров в корзине пользователя и расчета общей стоимости.
        """
        mock_redis.hgetall.return_value = {str(self.dish.id).encode(): b'2'}

        url = reverse('cart-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_price'], Decimal('20.00'))
        self.assertEqual(len(response.data['positions']), 1)
        self.assertEqual(response.data['positions'][0]['name'], 'Test Dish')
        self.assertEqual(response.data['positions'][0]['quantity'], 2)

    @patch('api.views.rd')
    def test_delete_dish_from_cart_remove_all(self, mock_redis):
        """
        Проверка удаления блюда из корзины пользователя, когда количество удаляемого блюда равно количеству в корзине.
        """
        mock_redis.hget.return_value = b'2'
        mock_redis.hdel.return_value = None

        url = reverse('cart-delete')
        data = {'dish_id': self.dish.id, 'quantity': 2}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        mock_redis.hdel.assert_called_with(f'cart:{self.user.id}', self.dish.id)


class OrderViewSetTest(APITestCase):

    def setUp(self):
        """
        Установка начальных данных для тестов.
        """
        self.user = CustomUser.objects.create_user(username='testuser', password='password123',
                                                   balance=Decimal('100.00'))
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.dish1 = Dish.objects.create(name="Test Dish 1", price=Decimal("10.00"), restaurant=self.restaurant)
        self.dish2 = Dish.objects.create(name="Test Dish 2", price=Decimal("20.00"), restaurant=self.restaurant)
        self.client.force_authenticate(user=self.user)

    @patch('api.views.rd')
    def test_create_order(self, mock_redis):
        """
        Проверка создания заказа и списания средств с баланса пользователя.
        """
        mock_redis.hgetall.return_value = {str(self.dish1.id).encode(): b'2', str(self.dish2.id).encode(): b'1'}
        mock_redis.delete.return_value = None

        url = reverse('order-list')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("60.00"))

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.items.count(), 2)

    @patch('api.views.rd')
    def test_create_order_insufficient_funds(self, mock_redis):
        """
        Проверка создания заказа при недостатке средств на балансе пользователя.
        """
        mock_redis.hgetall.return_value = {str(self.dish1.id).encode(): b'10'}  # Total price = 100.00
        mock_redis.delete.return_value = None

        self.user.balance = Decimal("50.00")
        self.user.save()

        url = reverse('order-list')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Сумма списания превышает средства на балансе')

    @patch('api.views.rd')
    def test_list_orders(self, mock_redis):
        """
        Проверка получения последних 10 заказов пользователя и расчета общей стоимости.
        """
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, dish=self.dish1, quantity=2)

        url = reverse('order-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_count'], 1)
        self.assertEqual(response.data['total_sum'], 20.00)
        self.assertEqual(len(response.data['last_orders']), 1)

    @patch('api.views.rd')
    def test_create_order_no_items_in_cart(self, mock_redis):
        """
        Проверка создания заказа, когда в корзине пользователя нет товаров.
        """
        mock_redis.hgetall.return_value = {}

        url = reverse('order-list')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 500)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Нет позиций в корзине для создания заказа')
