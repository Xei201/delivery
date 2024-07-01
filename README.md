# Food Ordering System

## Часть 1: Задача

Проектирование веб-приложения для заказа еды (по типу Яндекс Еды / Delivery Club). 

### Требования:
- Реализовать приложение на Django 4.0+ с использованием DRF. 
- Для модели пользователя сделать кастомный AbstractUser от джанги.
- Новая модель пользователя должена использоваться фреймворком по-умолчанию.
- Если пользователь не авторизован - все запросы выдают 403
- Аутентификация через сессию джанги.
- Прикручивать JWT токены и тд не нужно. Регистрацию, логин и тд делать не нужно, только запросы из задания. 
- Предусмотреть откат результатов запроса при непредвиенных ошибках (500) 
- Покрыть код тестами на основе TestCase-ов из rest_framework.test 
- Добавить конфигурацию докера с docker-compose для запуска приложения в докере

## Часть 2: Стек

Django + DRF + Redis + SQLite
На Django + DRF реализована основная логика приложения. Redis используется для кеширования и реализации корзины, 
чтобы уменьшить число обращение к БД. В качестве БД использовалась базовая SQLite, в идеале использовать PostgreSQL,
но в данной задаче это избытчно, единственное реализация поиска по названиям блюд хромает, так как у SQLite проблемы 
с регистрами, так что хоть реализован поиск без учёта регистра, но он работает как регистрозависимый. 

## Часть 3: Установка рабочего прототипа 

Скачайте проект.

В файле `.env` заполните все переменные окружения, я прикладываю сразу заполненный файл, хотя понятно, что так не стоит делать.

Для работы приложения необходимо предварительно установить [Docker Engine](https://docs.docker.com/engine/install/) 
и [Docker Compose](https://docs.docker.com/compose/install/).

После чего находясь в каталоге с файлом docker-compose.dev.yml выполните команду:

```js
 docker compose -f docker-compose.dev.yml up -d
```

В базу данных уже загружен минимальный набор объектов и юзер. Параметры юзера ниже:
```js
 Логин: xei
 Пароль: pass
```
## Часть 3: Тесты

Приложение покрыто тестами на основе TestCase-ов из rest_framework.test. Для запуска тестов перейдите в директорию `backend` и запустите тесты.
```js
cd backend
python manage.py test
```

## Часть 4: Реализация списка точек входа API


- `POST /api/v1/login/` - аутентификация пользователя.
- `POST /api/v1/logout/` - завершение сессии пользователя.
- `GET /api/v1/restaurants` - получить информацию о ресторанах и блюдах в них.
- `GET /api/v1/cart` - получить информацию о добавленных в корзину позициях и итоговой стоимости корзины.
- `POST /api/v1/cart/dish/add/` - добавление позиции в корзину.
- `POST /api/v1/cart/dish/delete/` - удаление позиции из корзины.
- `GET /api/v1/cart/orders` - получение последних 10 заказов.
- `POST /api/v1/cart/orders/` - создание на базе хранящихся в корзине позиций заказа и списания средств с баланса клиента.


### Пример работы

#### 1. `POST /api/v1/login/` - аутентификация пользователя.

Запрос:

```http
POST /api/v1/login/ HTTP/1.1
accept: application/json
content-type: application/json

{
    "username": "xei",
    "password": "pass"
}
```

Ответ:

```http
HTTP/1.1 200 OK
content-type: application/json
Cookies:
sessionid=abc123
csrftoken=xyz456
```

В дальнейших запросах применяем полученные `sessionid` и `csrftoken` для получения доступа к ресурсам.

#### 2. `POST /api/v1/logout/` - завершение сессии пользователя.

Запрос:

```http
POST /api/v1/logout/ HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456
```

Ответ:

```http
HTTP/1.1 200 OK
content-type: application/json
```

#### 3. `GET /api/v1/restaurants` - получить информацию о ресторанах и блюдах в них.

Запрос:

```http
GET /api/v1/restaurants?restaurant_id=1&dish_name=Биг HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456
```

Ответ:

```http
HTTP/1.1 200 OK
accept: application/json
[
    {
        "id": 1,
        "name": "Мак",
        "dishes": [
            {
                "id": 1,
                "name": "Биг Мак",
                "price": "344.00"
            },
            {
                "id": 2,
                "name": "Биг Тейсти",
                "price": "565.00"
            }
        ]
    }
]
```

#### 4. `GET /api/v1/cart` - получить информацию о добавленных в корзину позициях и итоговой стоимости корзины.

Запрос:

```http
GET /api/v1/cart HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456
```

Ответ:

```http
HTTP/1.1 200 OK
accept: application/json
{
    "total_price": 18527.0,
    "positions": [
        {
            "dish_id": 9,
            "name": "Рисовый вок",
            "quantity": 1,
            "price": 567.0
        },
        {
            "dish_id": 5,
            "name": "Рис Вкусный",
            "quantity": 2,
            "price": 690.0
        },
        {
            "dish_id": 3,
            "name": "Раки",
            "quantity": 5,
            "price": 17270.0
        }
    ]
}
```

#### 5. `POST /api/v1/cart/dish/add/` - добавление позиции в корзину.

Запрос:

```http
POST /api/v1/cart/dish/add/ HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456

{
    "dish_id": 9,
    "quantity": 399
}
```

Ответ:

```http
HTTP/1.1 200 OK
content-type: application/json
```

#### 6. `POST /api/v1/cart/dish/delete/` - удаление позиции в корзину.

Запрос:

```http
POST /api/v1/cart/dish/delete/ HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456

{
    "dish_id": 1,
    "quantity": 2
}
```

Ответ:

```http
HTTP/1.1 200 OK
content-type: application/json
```

#### 7. `GET /api/v1/cart/orders` - получение последних 10 заказов.

Запрос:

```http
GET /api/v1/cart/orders HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456
```

Ответ:

```http
HTTP/1.1 200 OK
accept: application/json

{
    "total_count": 1,
    "total_sum": 18527.0,
    "last_orders": [
        {
            "id": 1,
            "time": 1719849268,
            "total_price": 18527.0,
            "items": [
                {
                    "id": 1,
                    "dish": 9,
                    "price": 567.0,
                    "quantity": 1
                },
                {
                    "id": 2,
                    "dish": 5,
                    "price": 690.0,
                    "quantity": 2
                },
                {
                    "id": 3,
                    "dish": 3,
                    "price": 17270.0,
                    "quantity": 5
                }
            ]
        }
    ]
}
```

#### 8. `POST /api/v1/cart/orders/` - создание на базе хранящихся в корзине позиций заказа и списания средств с баланса клиента.

Запрос:

```http
POST /api/v1/cart/orders/ HTTP/1.1
accept: application/json
Cookies: sessionid=abc123
Headers: X-CSRFToken = xyz456

```

Ответ:

```http
HTTP/1.1 200 OK
content-type: application/json
```
