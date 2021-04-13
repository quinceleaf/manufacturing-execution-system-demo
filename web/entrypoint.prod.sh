#!/bin/bash

# if any of the commands in your code fails for any reason, the entire script fails
set -o errexit
# fail exit if one of your pipe command fails
set -o pipefail
# exits if any of your variables is not set
set -o nounset

export PATH="/home/app/web:/home/app/web/poetry:/home/app/web/.venv/bin:$PATH"

postgres_ready() {
/home/app/web/.venv./bin/python3 << END
import sys

import psycopg2

try:
    psycopg2.connect(
        dbname="${SQL_DATABASE}",
        user="${SQL_USER}",
        password="${SQL_PASSWORD}",
        host="${SQL_HOST}",
        port="${SQL_PORT}",
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)

END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

/home/app/web/.venv./bin/python3 manage.py makemigrations --noinput
/home/app/web/.venv./bin/python3 manage.py migrate --noinput
/home/app/web/.venv./bin/python3 manage.py collectstatic --noinput

exec "$@"