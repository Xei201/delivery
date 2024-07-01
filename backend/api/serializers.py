from rest_framework import serializers
from _decimal import Decimal


from core.models import Dish, Restaurant, Order
from core.models.order_item import OrderItem


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ['id', 'name', 'price']


class RestaurantSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'dishes']


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'dish', 'price', 'quantity']

    def get_price(self, obj: OrderItem) -> Decimal:
        # Метод для вычисления цены товара как произведение цены блюда и его количества
        return obj.quantity * obj.dish.price


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'time', 'total_price', 'items']

    def get_total_price(self, obj: Order) -> Decimal:
        # Метод для вычисления цены всего заказа как суммы цен всех позиций
        return sum(item.quantity * item.dish.price for item in obj.items.all())

    def get_time(self, obj: Order) -> int:
        return int(obj.created_at.timestamp())

# ниже сериализаторы для проверки входящие данных


class AddOrDeleteToCartSerializer(serializers.Serializer):
    dish_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_dish_id(self, value: int) -> int:
        # Метод провеляет существует ли данная позиция
        if not Dish.objects.filter(id=value).exists():
            raise serializers.ValidationError("Dish not found")
        return value


