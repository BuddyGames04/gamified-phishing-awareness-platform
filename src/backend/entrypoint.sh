#!/bin/sh
set -e

echo "Waiting for Postgres..."
until pg_isready -h "${POSTGRES_HOST:-db}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-devuser}" -d "${POSTGRES_DB:-l4proj}" >/dev/null 2>&1; do
  sleep 1
done

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
