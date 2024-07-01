#!/bin/sh
python manage.py collectstatic --noinput
python manage.py migrate
#python -m gunicorn -w 4 wsgi:application --bind 0.0.0.0:8000
python manage.py runserver 0.0.0.0:8000