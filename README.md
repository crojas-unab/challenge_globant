Globant Data Engineering Challenge

Este repositorio contiene la solución al desafío de ingeniería de datos de Globant. El proyecto está desarrollado con **FastAPI**, **SQLAlchemy**, **SQLite**, y **Pandas**, y tiene como objetivo simular una migración de datos desde archivos CSV hacia una base de datos relacional, junto con una serie de consultas analíticas a través de una API.

---

Estructura del Proyecto

```bash
.
├── app/
│   ├── __init__.py
│   ├── main.py           # Definición de la API con FastAPI
│   ├── models.py         # Definición de las tablas con SQLAlchemy
│   └── database.py       # Conexión e inicialización de la base de datos
├── requirements.txt      # Librerías necesarias para ejecutar el proyecto
├── README.md             # Este archivo
├── notebook_test.ipynb   # Notebook donde se realizan algunas pruebas en instalaciones



Funcionalidades
Sección 1 - API
Subida de datos desde CSV a la base de datos con endpoint /upload_csv/{table_name}.

Inserciones por lote hasta 1000 registros.

Tablas soportadas:

- departments
- jobs
- hired_employees

Sección 2 - SQL
Endpoints adicionales para consultas analíticas:

/metrics/hired-by-quarter?year=2021
Devuelve el número de empleados contratados por departamento y puesto, dividido por trimestre.

/metrics/departments-above-mean?year=2021
Devuelve los departamentos que contrataron más empleados que el promedio general en el año especificado.


Cómo ejecutar la aplicación

1: Entorno local
Clona el repositorio:

https://github.com/crojas-unab/challenge_globant.git

2: Instala las dependencias:
pip install -r requirements.txt    #esto lo puedes aplicar en el notebook_test.ipynb 

Ejecuta la aplicación:

uvicorn app.main:app --reload    #debera ejecutarse desde la ruta de la app

Accede a la API:

http://localhost:8000/docs




