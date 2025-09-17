#!/usr/bin/env bash
set -e

if [ -n "$DB_HOST" ]; then
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT ..."
  until nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
    sleep 1
  done
  echo "Postgres is up!"
fi

python manage.py migrate --noinput

exec "$@"