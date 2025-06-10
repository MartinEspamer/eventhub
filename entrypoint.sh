#!/bin/sh

# Termina el script si un comando falla
set -e

echo "Aplicando migraciones de la base de datos..."
python manage.py migrate --noinput

# El comando `exec "$@"` ejecuta el comando que se le pasa al script
exec "$@"