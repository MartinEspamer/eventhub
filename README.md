# Eventhub

Aplicación web para venta de entradas utilizada en la cursada 2025 de Ingeniería y Calidad de Software. UTN-FRLP

## Dependencias

-   python 3
-   Django
-   sqlite
-   playwright
-   ruff

## Instalar dependencias

`pip install -r requirements.txt`

## Iniciar la Base de Datos

`python manage.py migrate`

### Crear usuario admin

`python manage.py createsuperuser`

### Llenar la base de datos

`python manage.py loaddata fixtures/events.json`

## Iniciar app

`python manage.py runserver`

## Construir Imagen de Docker
`docker build -t eventhub .`

## Crear y correr Contenedor a partir de la Imagen
`docker run --name eventhub -p 8000:8000 --env-file .env -d eventhub`

## Acceder a la aplicacion (en el navegador)
`http://localhost:8000`


## Integrantes

-   Espamer Martin
-   Lanzzavecchia Cespedes Ignacio
-   Wacelinka Ariana
-   J. Bautista Cuenca
-   Molteni Baltazar
-   Ocampo Simon