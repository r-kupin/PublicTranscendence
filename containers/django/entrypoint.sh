#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate
exec daphne -b 0.0.0.0 -p 8000 simplified_prj.asgi:application
