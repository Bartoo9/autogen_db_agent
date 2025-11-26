#!/usr/bin/env bash
set -e

# Defaults come from .env via docker-compose
host="${DB_HOST:-postgres}"
port="${DB_PORT:-5432}"
user="${DB_USER:-postgres}"
dbname="${DB_NAME:-sakila}"
password="${DB_PASSWORD:-postgres}"

retries=30
count=0

echo "Waiting for Postgres at $host:$port ..."

until PGPASSWORD="$password" psql -h "$host" -U "$user" -d "$dbname" -c '\q' 2>/dev/null; do
  count=$((count+1))
  if [ $count -ge $retries ]; then
    echo "Postgres did not become available in time."
    exit 1
  fi
  sleep 1
done

echo "Postgres is ready — launching app"
python src/main.py
