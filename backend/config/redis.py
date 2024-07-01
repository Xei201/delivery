"""
Настройки Redis
"""

from django.conf import settings
from redis import ConnectionPool, Redis

redis_connection_pool = ConnectionPool.from_url(settings.URL_REDIS)


def get_redis_client() -> Redis:
    """
    Создает и возвращает экземпляр клиента Redis, используя заранее определенный пул подключений.

    Эта функция использует глобально определенный пул подключений Redis для создания нового
    экземпляра клиента Redis. Пул подключений помогает повторно использовать существующие подключения,
    что улучшает производительность и использование ресурсов.

    Примеры:
        >>> client = get_redis_client()
        >>> client.set('key', 'value')
        >>> client.get('key')
        b'value'

    Возвращает:
        Redis: Экземпляр клиента Redis, подключенный с использованием заранее определенного пула подключений.
    """
    return Redis(connection_pool=redis_connection_pool)
