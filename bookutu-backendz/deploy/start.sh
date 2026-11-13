#!/bin/sh
# Entry point for the backend image. SERVICE_ROLE selects what this container runs:
#   web    (default) - Django API + company dashboard via gunicorn
#   worker           - Celery worker with embedded beat scheduler
set -e

if [ "${SERVICE_ROLE:-web}" = "worker" ]; then
  echo "Starting Celery worker + beat"
  exec celery -A bookutu worker -B -l info --concurrency "${CELERY_CONCURRENCY:-2}" \
       --schedule /tmp/celerybeat-schedule
fi

# Persistent volume for uploads (bus photos, adverts, logos)
if [ -n "$MEDIA_ROOT" ]; then
  mkdir -p "$MEDIA_ROOT"
  if [ -z "$(ls -A "$MEDIA_ROOT" 2>/dev/null)" ] && [ -d media ]; then
    echo "Seeding media volume from image"
    cp -r media/. "$MEDIA_ROOT/"
  fi
fi

python manage.py migrate --noinput

# Brand-new empty database: create demo data so the app isn't blank.
# Set AUTO_SEED=false when importing existing data instead.
[ "${AUTO_SEED:-true}" = "true" ] && python manage.py shell -c "
from trips.models import Trip
from django.core.management import call_command
if not Trip.objects.exists():
    call_command('seed_demo')
"

# [::] = dual-stack, so Railway's private network (IPv6) can reach us too
exec gunicorn bookutu.wsgi:application --bind "[::]:${PORT:-8000}" \
     --workers "${WEB_CONCURRENCY:-3}" --timeout 60 --access-logfile -
