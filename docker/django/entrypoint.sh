#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser('${DJANGO_SUPERUSER_USERNAME}', 
                                '${DJANGO_SUPERUSER_EMAIL}', 
                                '${DJANGO_SUPERUSER_PASSWORD}')
EOF

# Collect static files
python manage.py collectstatic --no-input

# Create cache tables
python manage.py createcachetable

# Start Celery worker in background
celery -A config worker -l info &

# Start Celery beat in background
celery -A config beat -l info &

exec "$@"