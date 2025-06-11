# --- Etapa 1: Builder ---
# En esta etapa se instalan las dependencias
FROM python:3.13-slim-bullseye AS builder

# Establece las variables de entorno para evitar la creación de archivos .pyc y para que Python no escriba bytecode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Establece el directorio de trabajo
WORKDIR /eventhub

# Instala las dependencias en una ubicación que copiaremos luego
RUN pip install --upgrade pip
COPY requirements-docker.txt .
RUN pip install --target=/eventhub/deps -r requirements-docker.txt


# --- Etapa 2: Final ---
# Esta es la imagen final, mucho más limpia y ligera
FROM python:3.13-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /eventhub

# Copia solo las dependencias instaladas desde la etapa 'builder'
COPY --from=builder /eventhub/deps /usr/local/lib/python3.13/site-packages

# Copia el código de la aplicación
COPY . .

# Reúne los archivos estáticos en un solo directorio para producción
RUN python manage.py collectstatic --noinput

# Copia y da permisos de ejecución al script de entrada
COPY ./entrypoint.sh /eventhub/entrypoint.sh
RUN chmod +x /eventhub/entrypoint.sh

# Expone el puerto 
EXPOSE 8000

# Establece el script de entrada que se ejecutará al iniciar el contenedor
ENTRYPOINT ["/eventhub/entrypoint.sh"]

# Comando por defecto para el servidor. Debe escuchar en 0.0.0.0
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]