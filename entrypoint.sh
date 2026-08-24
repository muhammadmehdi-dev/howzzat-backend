#!/usr/bin/env bash
set -e

echo "Running database migrations..."
python manage.py makemigrations api
python manage.py migrate

echo "Creating superuser if not exists..."
export DJANGO_SUPERUSER_PASSWORD=${ADMIN_PASSWORD:-admin}
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@example.com
python manage.py createsuperuser --noinput || echo "Superuser already exists."

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django server..."
exec gunicorn howwzat_backend.wsgi:application --bind 0.0.0.0:8000
