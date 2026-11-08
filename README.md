# Agenda de Contactos con Acceso Aleatorio

Aplicación de escritorio desarrollada en Python con Tkinter para administrar una agenda de contactos almacenada en un archivo de registros de tamaño fijo (120 bytes en UTF-8). Permite posicionamiento directo mediante seek() y tell(), búsquedas indexadas en JSON, verificación de integridad con hash SHA-256, exportación a JSON/PDF y generación de respaldos comprimidos en ZIP.

## Requisitos
- Python 3.12 o superior
- Librería reportlab (para la generación del reporte PDF)
- tkinter (incluido por defecto en la instalación estándar de Python)

## Instalación
1. Clonar el repositorio o ubicarse en la carpeta raíz del proyecto:
   Correr el programa desde main.py