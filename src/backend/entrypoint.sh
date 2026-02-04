#!/bin/sh
set -e

echo "Waiting for Postgres..."
until python -c "import psycopg2; psycopg2.connect(
    dbname='${POSTGRES_DB}', user='${POSTGRES_USER}', password='${POSTGRES_PASSWORD}', host='db', port=5432
)" >/dev/null 2>&1; do
  sleep 1
done

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
