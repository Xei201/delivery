from _decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.db.models import Sum, F, Prefetch, QuerySet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .serializers import RestaurantSerializer, OrderSerializer, AddOrDeleteToCartSerializer
from config.redis import get_redis_client
from core.models import Restaurant, Dish, Order

rd = get_redis_client()


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request) -> Response:
        """
        Метод отвечает за аутентификацию пользователя и старт сессии
        :param request:
        :return: статус аутентификации
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'detail': 'Successfully logged in'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request) -> Response:
        """
        Метод отвечает за лоаут пользователя
        :param request:
        :return: статус разавторизации
        """
        logout(request)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

    def get_queryset(self) -> QuerySet:
        """
        Подбор списка ресторанов с учётом параметров фильтрации
        """
        queryset = super().get_queryset()
        dish_name = self.request.query_params.get('dish_name')
        restaurant_id = self.request.query_params.get('restaurant_id')

        # добавлена простая проверка ID ресторана, по факту можно использовать django filter

        if restaurant_id:
            if not restaurant_id.isdigit():
                raise PermissionDenied(detail="Указан не корректный ID ресторана")

            queryset = queryset.filter(id=restaurant_id)

        # Фильтрация по имени блюда
        if dish_name:
            queryset = queryset.filter(
                dishes__name__icontains=dish_name
            ).prefetch_related(
                Prefetch("dishes", queryset=Dish.objects.filter(name__icontains=dish_name))
            )

        # Проверка наличия объектов
        if not queryset.exists():
            raise PermissionDenied(detail="Ресторан не найден или у вас нет разрешения на его просмотр.")
        return queryset.distinct()


class CartViewSet(viewsets.ViewSet):

    def list(self, request) -> Response:
        """
        Получает все товары в корзине пользователя и рассчитывает общую стоимость.
        """
        user_id = request.user.id
        cart_items = rd.hgetall(f'cart:{user_id}')
        cart_data = []
        total_price = Decimal("0.00")
        for dish_id, quantity in cart_items.items():

            dish = Dish.objects.get(id=dish_id)
            quantity = int(quantity)
            item_total_price = dish.price * quantity
            total_price += item_total_price
            cart_data.append({
                'dish_id': dish.id,
                'name': dish.name,
                'quantity': quantity,
                'price': item_total_price,
            })
        return Response({'total_price': total_price, 'positions': cart_data})

    @action(detail=False, methods=['post'], url_path='dish/add')
    def add(self, request) -> Response:
        """
        Добавление блюда в корзину пользователя.
        """
        serializer = AddOrDeleteToCartSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id
            dish_id = request.data.get('dish_id')
            quantity = int(request.data.get('quantity'))
            rd.hincrby(f'cart:{user_id}', dish_id, quantity)
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='dish/delete')
    def delete(self, request) -> Response:
        """
        Удаление блюда из корзины пользователя.
        """
        serializer = AddOrDeleteToCartSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.user.id
            dish_id = request.data.get('dish_id')
            quantity = int(request.data.get('quantity'))
            current_quantity = int(rd.hget(f'cart:{user_id}', dish_id))
            if current_quantity <= quantity:
                rd.hdel(f'cart:{user_id}', dish_id)
            else:
                rd.hincrby(f'cart:{user_id}', dish_id, -quantity)
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(viewsets.ViewSet):

    def list(self, request) -> Response:
        """
        Получение последних 10 заказов пользователя и расчёт общей стоимости.
        """
        orders = Order.objects.filter(user__id=request.user.id).prefetch_related('items__dish').annotate(
            total_price=Sum(F('items__quantity') * F('items__dish__price'))
        ).order_by('-created_at')[:10]
        serializer = OrderSerializer(orders, many=True)
        total_count = orders.count()
        total_sum = sum(order.total_price for order in orders)
        response_data = {
            "total_count": total_count,
            "total_sum": total_sum,
            "last_orders": serializer.data
        }
        return Response(response_data)

    @transaction.atomic
    def create(self, request) -> Response:
        """
        Создание на основе данных корзины пользователя заказа и списание средств в счёт оплаты заказа
        """
        try:
            user_id = request.user.id
            cart_items = rd.hgetall(f'cart:{user_id}')
            if not cart_items:
                raise Exception('Нет позиций в корзине для создания заказа')

            total_price = Decimal("0.00")
            order_items = []
            for dish_id, quantity in cart_items.items():
                dish = Dish.objects.get(id=dish_id)
                quantity = int(quantity)
                item_total_price = dish.price * quantity
                total_price += item_total_price
                order_items.append({
                    'dish_id': dish.id,
                    'quantity': quantity,
                })

            order = Order.objects.create(user=request.user)
            for item in order_items:
                order.items.create(
                    dish_id=item['dish_id'],
                    quantity=item['quantity'],
                )

            request.user.write_off_balance(total_price)

            # выполняем очистку корзины только после успешного списания средств с баланса,
            # остальную атомарность покрывает transaction.atomic
            rd.delete(f'cart:{user_id}')

        except Exception as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)

