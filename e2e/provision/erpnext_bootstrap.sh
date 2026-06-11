#!/usr/bin/env bash
# ERPNext first-boot bootstrap for the e2e harness.
#
# On a fresh `erpnext-sites` volume this creates the site `kontablo.localhost`,
# installs the erpnext app, and enables the REST API. On subsequent boots the
# site already exists, so it just starts the web server.
#
# This is the single automated entrypoint; if it fails in your environment,
# e2e/README.md documents the exact manual `bench` commands to run instead.
set -euo pipefail

cd /home/frappe/frappe-bench

SITE="kontablo.localhost"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin}"
DB_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-admin}"

# Point bench at the compose datastores.
bench set-config -g db_host "${DB_HOST:-erpnext-db}" || true
bench set-config -g redis_cache "redis://${REDIS_CACHE:-erpnext-redis:6379}" || true
bench set-config -g redis_queue "redis://${REDIS_QUEUE:-erpnext-redis:6379}" || true
bench set-config -g redis_socketio "redis://${REDIS_QUEUE:-erpnext-redis:6379}" || true

if [ ! -d "sites/${SITE}" ]; then
  echo "[bootstrap] creating site ${SITE}"
  bench new-site "${SITE}" \
    --no-mariadb-socket \
    --admin-password "${ADMIN_PASSWORD}" \
    --db-root-password "${DB_ROOT_PASSWORD}" \
    --install-app erpnext
  bench --site "${SITE}" set-config developer_mode 0
  bench --site "${SITE}" enable-scheduler
fi

bench use "${SITE}"
echo "[bootstrap] starting web server on :8080"
exec bench serve --port 8080
